import base64
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import gum
from gum import C, G, V, em, px
from gum.dem import DEMOS
from gum.gum import server
from gum.utl import Fun, stringify

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        server.close()

    def test_import_and_construction_without_runtime(self):
        env = {**os.environ, 'GUM_JSX_RUNTIME': '/missing/node'}
        script = "import gum; print(gum.G.Text('Hello')); assert gum.gum.server.proc is None"
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                                env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Hello', result.stdout)

    def test_serialization_and_symbolic_variables(self):
        value = V.sample([1, 2])
        code = G.Gum(G.Text(value[0] + 2), vars=[value])
        svg = gum.evaluate(code, text_mode='live')
        self.assertIn('>3<', svg)
        self.assertEqual(stringify(1.23456789012345), '1.23456789012345')
        self.assertEqual(stringify(float('nan')), 'NaN')
        comparison = C('"hello"') == 'hello'
        self.assertEqual(gum.evaluate('return ' + str(comparison)), 'true')
        self.assertEqual(str(Fun(lambda x: [x, True, None])), '(x) => ([x, true, null])')
        self.assertEqual(json.loads(gum.evaluate('return ' + stringify({'a"b': 1}))), {'a"b': 1})

    def test_escaped_text_and_props(self):
        text = 'A < B & "quotes" {braces} \\ slash'
        svg = gum.evaluate(G.Text(text, id='a"b'), text_mode='live')
        root = ET.fromstring(svg)
        labels = root.findall('.//{http://www.w3.org/2000/svg}text')
        self.assertEqual(''.join(''.join(label.itertext()) for label in labels), text)

    def test_viewport_and_source_sizing(self):
        source = G.Page(G.Rect(fill=C.red), width=px(120), height=px(60))
        root = ET.fromstring(gum.evaluate(source))
        self.assertEqual((root.get('width'), root.get('height')), ('120', '60'))
        root = ET.fromstring(gum.evaluate(source, width=80, height=40))
        self.assertEqual((root.get('width'), root.get('height')), ('80', '40'))
        root = ET.fromstring(gum.evaluate(G.Rect(aspect=2), width=100))
        self.assertEqual((root.get('width'), root.get('height')), ('100', '50'))
        root = ET.fromstring(gum.evaluate(G.Rect()))
        self.assertEqual((root.get('width'), root.get('height')), ('640', '480'))

    def test_theme_precedence_and_background(self):
        source = G.Page(G.Rect(fill='theme:foreground'), theme='light')
        kitty = gum.evaluate(source, width=8, height=4, output_format='pixels')
        self.assertEqual(kitty.getpixel((4, 2))[:3], (0, 0, 0))
        dark = gum.evaluate(source, width=8, height=4, output_format='pixels', theme='dark')
        self.assertEqual(dark.getpixel((4, 2))[:3], (255, 255, 255))
        clear = G.Rect(fill='none', stroke='none')
        image = gum.evaluate(clear, width=8, height=4, output_format='png', background='#ff0000')
        self.assertEqual(image.convert('RGBA').getpixel((4, 2)), (255, 0, 0, 255))
        svg = gum.evaluate(clear, background='#ff0000')
        self.assertIn('fill="#ff0000"', svg)

    def test_binary_outputs_and_sampling(self):
        source = G.Rect(fill=C.blue)
        image = gum.evaluate(source, width=30, height=18, output_format='png', ratio=2)
        self.assertEqual(image.size, (60, 36))
        crop = dict(x=1, y=2, width=7, height=3)
        image = gum.evaluate(source, width=30, height=18, output_format='pixels', select=crop, ratio=2)
        self.assertEqual(image.size, (14, 6))
        self.assertTrue(gum.render(source, width=30, height=18).startswith(b'\x89PNG'))
        self.assertTrue(gum.evaluate(source, width=120, height=120, output_format='pdf').startswith(b'%PDF'))
        self.assertTrue(gum.evaluate(source, width=120, height=120, output_format='pptx').startswith(b'PK'))
        self.assertIn('size', json.loads(gum.evaluate(source, output_format='json')))

    @unittest.skipUnless(importlib.util.find_spec('numpy'), 'numpy is optional')
    def test_pixel_array_orientation_and_kitty(self):
        import numpy as np
        source = G.Group(
            G.Rect(width=0.5, height=1, fill='#ff0000', stroke='none'),
            G.Rect(width=0.5, height=1, pos=(0.5, 0), anchor='start',
                   fill='#0000ff', stroke='none'),
        )
        pixels = gum.evaluate(source, width=12, height=6, output_format='pixels', return_format='numpy')
        self.assertEqual(pixels.shape, (6, 12, 4))
        self.assertEqual(pixels[3, 2].tolist(), [255, 0, 0, 255])
        self.assertEqual(pixels[3, 9].tolist(), [0, 0, 255, 255])
        kitty = gum.evaluate_pixels(pixels)
        self.assertIn('s=12,v=6', kitty)
        encoded = kitty.split(';', 1)[1][:-2]
        self.assertEqual(base64.b64decode(encoded), pixels.tobytes())
        with self.assertRaisesRegex(ValueError, 'uint8'):
            gum.evaluate_pixels(pixels.astype(float))
        with self.assertRaisesRegex(ValueError, 'shape'):
            gum.evaluate_pixels(pixels[:, :, :3])

    def test_math_and_modern_elements(self):
        source = G.HStack(
            G.Frac(G.MathSpan('1'), G.MathSpan('2')),
            G.Tex(r'\sqrt{x^2 + y^2}'), gap=em(1),
        )
        svg = gum.evaluate(source)
        self.assertIn('<path', svg)
        self.assertGreater(len(gum.render(source)), 100)
        line = G.Line(from_=(0, 0), to=(1, 1))
        self.assertIn('from={', str(line))
        self.assertIn('<path', gum.evaluate(line))
        self.assertIn('<path', gum.evaluate(G.Polyline([(0, 0), (1, 1), (0, 1)])))

    def test_error_recovery_seed_and_restart(self):
        with self.assertRaises(gum.GumError):
            gum.evaluate('<Invalid>')
        self.assertIn('<svg', gum.evaluate(G.Circle()))
        with self.assertRaises(gum.GumError) as context:
            gum.evaluate(' ')
        self.assertEqual(context.exception.error_type, 'NOCODE')
        code = 'return <Text>{random()}</Text>'
        self.assertEqual(gum.evaluate(code, seed=7), gum.evaluate(code, seed=7))
        self.assertNotEqual(gum.evaluate(code, seed=7), gum.evaluate(code, seed=9))
        server.proc.kill()
        server.proc.wait()
        self.assertIn('<svg', gum.evaluate(G.Circle()))

    def test_concurrent_binary_requests(self):
        def render(width):
            return gum.evaluate(G.Rect(), width=width, height=17, output_format='png').size
        with ThreadPoolExecutor(max_workers=4) as pool:
            sizes = list(pool.map(render, range(20, 32)))
        self.assertEqual(sizes, [(width, 17) for width in range(20, 32)])

    def test_png_input(self):
        png = gum.render(G.Rect(), width=8, height=4)
        self.assertTrue(gum.evaluate_png(png).startswith('\x1b_Gf=100'))

    def test_notebook_display_requests_svg(self):
        if not importlib.util.find_spec('IPython'):
            self.skipTest('IPython is optional')
        with patch('gum.utl.is_notebook', return_value=True), \
                patch('IPython.display.display_svg') as display_svg:
            G.Text('Notebook')._ipython_display_()
        self.assertTrue(display_svg.call_args.args[0].startswith('<svg'))
        self.assertTrue(display_svg.call_args.kwargs['raw'])

    def test_all_demos_render(self):
        for name in DEMOS:
            with self.subTest(demo=name):
                source = gum.demo(name)
                self.assertEqual(ET.fromstring(gum.evaluate(source)).tag,
                                 '{http://www.w3.org/2000/svg}svg')
                image = gum.evaluate(source, output_format='png')
                self.assertIsNotNone(image.convert('RGBA').getbbox())

    def test_cli_binary_and_svg_output(self):
        result = subprocess.run(
            [sys.executable, '-m', 'gum', '-d', 'plot', '-f', 'svg', '-W', '320'],
            cwd=ROOT, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(ET.fromstring(result.stdout).get('width'), '320')
        result = subprocess.run(
            [sys.executable, '-m', 'gum', '-f', 'png', '-W', '12', '-H', '6'],
            input=b'<Rect />', cwd=ROOT, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertTrue(result.stdout.startswith(b'\x89PNG'))

    @unittest.skipUnless(importlib.util.find_spec('pandas'), 'pandas is optional')
    def test_dataframe_plots_and_categories(self):
        import pandas as pd
        frame = pd.DataFrame([[1, 2, 3], [2, 3, 4], [3, float('nan'), 5]],
                             columns=['has spaces', 'has spaces', 'class'])
        frame.index.name = 'bad index name'
        for plot in (gum.lines(frame), gum.lines(frame, spline=True), gum.points(frame)):
            self.assertIn('<svg', gum.evaluate(plot))
        for direction in ('vertical', 'horizontal'):
            bars = gum.bars(pd.Series([3, 5], index=['A & B', 'C']), direction=direction)
            root = ET.fromstring(gum.evaluate(bars, text_mode='live'))
            self.assertIn('A & B', ''.join(root.itertext()))
            rects = root.findall('.//{http://www.w3.org/2000/svg}rect')
            self.assertGreaterEqual(sum(float(rect.get('width', 0)) > 0 for rect in rects), 2)


if __name__ == '__main__':
    unittest.main()
