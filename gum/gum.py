# Python interface to the persistent Gum rendering process.
import atexit
import io
import json
import os
import shutil
import subprocess
import sys
import threading
from collections import deque
from PIL import Image

LIB_PATH = os.path.dirname(__file__)
GUM_PATH = os.path.join(LIB_PATH, 'js', 'pipe.ts')
RUN_ENV = 'GUM_JSX_RUNTIME'
RUN_DEFAULT = 'bun'


def is_numpy_array(value):
    cls = type(value)
    return cls.__module__ == 'numpy' and cls.__name__ == 'ndarray'


def is_torch_tensor(value):
    cls = type(value)
    return cls.__module__ == 'torch' and cls.__name__ == 'Tensor'


def decode_png(data, return_format='pil'):
    if return_format == 'bytes':
        return data
    if return_format != 'pil':
        raise ValueError(f'Invalid return format for PNG: {return_format}')
    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def decode_pixels(data, size, return_format='pil'):
    # Wire dimensions are (width, height); array dimensions are (height, width).
    width, height = size
    if return_format == 'pil':
        return Image.frombytes('RGBA', (width, height), data)
    if return_format == 'numpy':
        import numpy as np
        return np.frombuffer(bytearray(data), dtype=np.uint8).reshape(height, width, 4)
    if return_format == 'torch':
        import torch
        return torch.frombuffer(bytearray(data), dtype=torch.uint8).reshape(height, width, 4)
    if return_format == 'bytes':
        return data
    raise ValueError(f'Invalid return format for pixels: {return_format}')


def encode_png(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


class GumErrorType:
    PARSE = 'PARSE'
    LAYOUT = 'LAYOUT'
    NOCODE = 'NOCODE'
    NORETURN = 'NORETURN'
    NOELEMENT = 'NOELEMENT'
    STRICT = 'STRICT'


class GumError(Exception):
    def __init__(self, error_type, error_message, error_stack=None):
        self.error_type = error_type
        self.error_message = error_message
        self.error_stack = error_stack
        super().__init__(f'{error_type}: {error_message}')


class GumUnixPipe:
    def __init__(self):
        # JSX construction and importing gum do not require a running backend.
        self.proc = None
        self.debug = True
        self._lock = threading.RLock()
        self._pump_thread = None
        self._errors = deque(maxlen=20)

    def init(self):
        runtime = os.environ.get(RUN_ENV) or RUN_DEFAULT
        if shutil.which(runtime) is None:
            raise RuntimeError(
                f'Gum requires Bun 1.4.2 or newer; {runtime!r} was not found. '
                f'Set {RUN_ENV} to the Bun executable.'
            )
        self._errors.clear()
        self.proc = subprocess.Popen(
            [runtime, GUM_PATH], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self._start_pump_loop()

    def _start_pump_loop(self):
        # Capture this process so restarts cannot redirect the old reader.
        stream = self.proc.stderr

        def pump_loop():
            for line in stream:
                message = line.decode(errors='replace').rstrip()
                self._errors.append(message)
                if self.debug:
                    print(f'[gum server] {message}', file=sys.stderr)

        self._pump_thread = threading.Thread(target=pump_loop, daemon=True)
        self._pump_thread.start()

    def connection_error(self):
        if self._pump_thread:
            self._pump_thread.join(timeout=0.2)
        details = '\n'.join(self._errors)
        return RuntimeError(
            'Gum backend closed the connection. Install its dependencies with '
            f'`bun install --cwd {os.path.join(LIB_PATH, "js")}`.\n{details}'
        )

    def read_exact(self, length):
        chunks = []
        while length:
            chunk = self.proc.stdout.read(length)
            if not chunk:
                raise self.connection_error()
            chunks.append(chunk)
            length -= len(chunk)
        return b''.join(chunks)

    def post(self, return_format='pil', **request):
        # A request and its binary response are one indivisible transaction.
        with self._lock:
            return self._post(return_format, request)

    def _post(self, return_format, request):
        data = request['data']
        if isinstance(data, Image.Image):
            if request.get('input_format') == 'pixels':
                request['size'] = data.size
                data = data.convert('RGBA').tobytes()
            else:
                data = encode_png(data)
        elif is_numpy_array(data) or is_torch_tensor(data):
            if is_torch_tensor(data):
                data = data.detach().cpu().contiguous().numpy()
            if data.ndim != 3 or data.shape[2] != 4 or str(data.dtype) != 'uint8':
                raise ValueError('Pixel arrays must have shape (height, width, 4) and dtype uint8')
            request['size'] = (data.shape[1], data.shape[0])
            data = data.tobytes()
        request['data'] = data

        # Normalize binary input before serializing the JSON header.
        if isinstance(data, (bytes, bytearray, memoryview)):
            binary = bytes(request.pop('data'))
            request['bytes_length'] = len(binary)
        else:
            binary = None
        header = {key: value for key, value in request.items() if value is not None}
        payload = (json.dumps(header) + '\n').encode()
        if self.proc is None or self.proc.poll() is not None:
            self.close()
            self.init()
        try:
            self.proc.stdin.write(payload)
            if binary is not None:
                self.proc.stdin.write(binary)
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise self.connection_error() from error

        reply = self.proc.stdout.readline()
        if not reply:
            raise self.connection_error()
        response = json.loads(reply)
        fmt, data = response['format'], response['data']
        if fmt == 'error':
            raise GumError(data['error'], data['message'], data.get('stack'))
        if fmt in ('png', 'pixels', 'pdf', 'pptx'):
            binary = self.read_exact(data['length'])
            if fmt == 'png':
                return decode_png(binary, return_format)
            if fmt == 'pixels':
                return decode_pixels(binary, data['size'], return_format)
            return binary
        if fmt in ('string', 'kitty'):
            return data
        raise ValueError(f'Invalid output format: {fmt}')

    def close(self):
        with self._lock:
            if self.proc is None:
                return
            proc, self.proc = self.proc, None
            try:
                proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            if self._pump_thread:
                self._pump_thread.join(timeout=1)
            proc.stdout.close()
            proc.stderr.close()
            self._pump_thread = None

    def restart(self):
        with self._lock:
            self.close()
            self.init()


server = GumUnixPipe()
atexit.register(server.close)


def restart():
    server.restart()


def set_debug(debug=True):
    server.debug = debug


def evaluate(jsx, size=None, output_format='svg', **kwargs):
    """Render JSX. SVG is text; PNG/pixels default to PIL; PDF/PPTX return bytes."""
    if size is not None:
        if 'width' in kwargs or 'height' in kwargs:
            raise ValueError('Use either size or width/height')
        if isinstance(size, (tuple, list)):
            if len(size) != 2:
                raise ValueError('size must be a width or (width, height) in pixels')
            kwargs['width'], kwargs['height'] = size
        else:
            kwargs['width'] = size
    return server.post(data=str(jsx), output_format=output_format, **kwargs)


def render(jsx, **kwargs):
    """Render JSX as PNG bytes."""
    return evaluate(jsx, output_format='png', return_format='bytes', **kwargs)


def evaluate_svg(svg, output_format='svg', **kwargs):
    """Return SVG text; current Gum no longer rasterizes existing SVG strings."""
    return server.post(data=svg, input_format='svg', output_format=output_format, **kwargs)


def evaluate_png(png, **kwargs):
    return server.post(data=png, input_format='png', output_format='kitty', **kwargs)


def evaluate_pixels(pixels, **kwargs):
    return server.post(data=pixels, input_format='pixels', output_format='kitty', **kwargs)


def display(jsx, **kwargs):
    print(evaluate(jsx, output_format='kitty', **kwargs))


def display_svg(svg, **kwargs):
    print(evaluate_svg(svg, output_format='kitty', **kwargs))


def display_png(png, **kwargs):
    print(evaluate_png(png, **kwargs))


def display_pixels(pixels, **kwargs):
    print(evaluate_pixels(pixels, **kwargs))


def display_file(path, **kwargs):
    with open(path, encoding='utf-8') as source:
        display(source.read(), **kwargs)
