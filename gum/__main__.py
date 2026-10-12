# Render a demo or JSX from stdin using the same viewport options as Gum.
import argparse
import os
from pathlib import Path
import subprocess
import sys

from .dem import demo, DEMOS
from .gum import evaluate, LIB_PATH, RUN_DEFAULT, RUN_ENV


def main():
    parser = argparse.ArgumentParser(
        description='Render Gum JSX from stdin, or a Python demo.',
        epilog='Example: python -m gum -d plot -o plot.png',
    )
    parser.add_argument('-d', '--demo', choices=DEMOS, help='run a built-in demo')
    parser.add_argument('-W', '--width', type=float, help='viewport width in pixels')
    parser.add_argument('-H', '--height', type=float, help='viewport height in pixels')
    parser.add_argument('-r', '--ratio', type=float, default=1, help='raster sampling ratio')
    parser.add_argument('-t', '--theme', choices=['light', 'dark'], help='override the source theme')
    parser.add_argument('-b', '--background', help='viewport background color')
    parser.add_argument('-f', '--format', choices=['svg', 'png', 'kitty', 'pdf', 'pptx', 'tree', 'json'])
    parser.add_argument('-o', '--output', type=Path, help='output file; its suffix selects the format')
    parser.add_argument('--text-mode', choices=['path', 'live', 'mixed'])
    parser.add_argument('--page', type=int, help='select one document page, starting at 1')
    parser.add_argument('--install', action='store_true', help='install the Bun backend dependencies')
    args = parser.parse_args()

    if args.install:
        runtime = os.environ.get(RUN_ENV) or RUN_DEFAULT
        try:
            subprocess.run(
                [runtime, 'install', '--force', '--frozen-lockfile',
                 '--cwd', os.path.join(LIB_PATH, 'js')], check=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            parser.exit(1, f'Backend installation failed: {error}\n')
        return
    fmt = args.format or (args.output.suffix.lstrip('.') if args.output else 'kitty')
    code = demo(args.demo) if args.demo else sys.stdin.read()
    try:
        data = evaluate(
            code, width=args.width,
            height=args.height, ratio=args.ratio, theme=args.theme,
            background=args.background, output_format=fmt,
            return_format='bytes', text_mode=args.text_mode, page=args.page,
        )
    except Exception as error:
        parser.exit(1, f'{error}\n')
    if args.output:
        if isinstance(data, bytes):
            args.output.write_bytes(data)
        else:
            args.output.write_text(data, encoding='utf-8')
    elif isinstance(data, bytes):
        sys.stdout.buffer.write(data)
    else:
        print(data)


if __name__ == '__main__':
    main()
