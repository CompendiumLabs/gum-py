<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/logo-dark.svg" />
    <img src="images/logo.svg" alt="Gum" width="300" />
  </picture>
  <br /><br />
  <img src="images/nexus.svg" alt="Layered red-to-blue wave packets" width="250" />
  <br /><br />
</div>

Python constructors and rendering for [Gum](https://github.com/CompendiumLabs/gum-jsx),
a language for creating vector graphics. Build plots, diagrams, documents, and math in
Python, then render SVG, PNG, RGBA pixels, PDF, PowerPoint, or kitty terminal graphics.
Elements also display in Jupyter notebooks.

This adapter targets the Gum **2.1.0** libraries. Rendering uses **Node.js 24 or
newer**. The Python wheel includes the compiled JavaScript backend and fonts.
`GUM_JSX_RUNTIME` can point to a different Node.js executable.

## Installation

```sh
python -m pip install 'gum-py'
```

The base package requires only Pillow. Installing a wheel needs no
JavaScript dependency installation or build step. Importing `gum` and constructing
JSX do not start Node.js. The renderer starts on the first render request and is
reused until Python exits. Install the `gum-py[plotting]` target to use NumPy and
pandas for the high-level plotting helpers.

## Python API

```python
import gum
from gum import G, C, px, em

plot = G.Plot(
    G.SymLine(
        fy=C.sin, xlim=(0, 2*C.pi),
        stroke=C.blue, stroke_width=px(2),
    ),
    grid=True, aspect=C.phi, font_size=px(22),
    xlabel='Phase', ylabel='Amplitude',
)

svg = gum.evaluate(plot)                        # SVG string
png = gum.render(plot, width=800)                # PNG bytes
image = gum.evaluate(plot, output_format='png')  # PIL image
gum.display(plot)                               # kitty terminal graphics
jsx = str(plot)                                 # JSX source
```

In a notebook, leaving an element as the last expression displays its SVG.
Constructors live in `gum.G` or `gum.gen`. `C` references Gum constants, functions,
and expressions; `V.name(data)` declares a JavaScript variable when included in
`G.Gum(element, vars=[variable])`. Python lambdas become JavaScript functions:

```python
decay = lambda x: C.exp(-x/2) * C.sin(3*x)
curve = G.SymLine(fy=decay, xlim=(0, 2*C.pi), samples=200)
```

Use `px(20)` for pixel lengths, `em(1)` for font-relative lengths, and fractions
such as `0.5` for relative lengths. Props use snake_case in Python and become
kebab-case JSX. A trailing underscore escapes a Python keyword, for example
`G.Line(from_=(0, 0), to=(1, 1))`.

### Rendering options

`gum.evaluate(source, **options)` accepts Python elements or a JSX source string.

| Option | Meaning |
|---|---|
| `output_format` | `svg` (default), `png`, `pixels`, `kitty`, `pdf`, `pptx`, `tree`, or `json` |
| `page` | Select one document page, starting at 1; required for multi-page SVG/raster/kitty output |
| `width`, `height` | Independent viewport overrides in pixels |
| `ratio` | PNG/pixel/kitty sampling ratio, default 1; does not change layout |
| `select` | Raster crop dictionary with `x`, `y`, `width`, `height` |
| `theme` | Explicit `light` or `dark` override |
| `background` | Viewport background; transparent if omitted |
| `text_mode` | `path`, `live`, or `mixed`; raster output always uses paths |
| `seed` | Seed for the evaluation's independent random stream |
| `title`, `id_prefix`, `precision` | Current Gum export metadata and SVG/numeric output options |
| `return_format` | PNG: `pil` or `bytes`; pixels: `pil`, `numpy`, `torch`, or `bytes` |

With no width/height override, Gum offers a 640 × 480 layout budget. Explicit
source sizes win, short content hugs its contents, and tall content may grow.
One width override leaves height natural. Themes default to light for file
formats and dark for kitty, while source `<Page theme=...>` wins unless a theme
is explicitly passed to Python.

PDF and PPTX return bytes. SVG, tree, JSON, and kitty return strings. PDF defaults
to live text and PPTX to mixed text; PPTX requires dimensions of at least 96 pixels
on each side. `G.Document` exports all its pages to PDF/PPTX; `page=...` exports
just the selected page. Video/MP4 and file-based deck assembly remain available
through the Gum CLI.

`evaluate_png()` and `evaluate_pixels()` encode existing PNG/RGBA data for kitty;
the corresponding `display_*()` functions print it. Pixel buffers use
`size=(width, height)`, while NumPy/Torch arrays use `(height, width, 4)` with
`uint8` channels. PIL images are accepted too.

### Pages and documents

`G.Page` sets a viewport's size and style. `G.Document` groups pages for export,
and its props provide defaults that individual pages can override. Slides are
also pages and can be children of a document.

```python
document = G.Document(
    G.Page(G.Text('First page')),
    G.Page(G.Text('Second page')),
    width=px(640), height=px(480), title='Example',
)
pdf = gum.evaluate(document, output_format='pdf')
pptx = gum.evaluate(document, output_format='pptx')
preview = gum.evaluate(document, page=2)
```

JSON output for a document contains `title` (when set) and `pages`; selecting a
page returns that page's fragment. Tree output lists each page.

## Pandas integration

```python
import numpy as np
import pandas as pd
from gum import lines, points, bars

phase = np.linspace(0, 2*np.pi, 100)
frame = pd.DataFrame({'sin': np.sin(phase), 'cos': np.cos(phase)}, index=phase)
lines(frame)
points(frame, point_size=px(5))
bars(pd.Series({'A': 3, 'B': 8, 'C': 5}), fill=C.blue)
```

Column labels may contain spaces, punctuation, or duplicate names. The adapter
uses separate, stable JavaScript identifiers. Bars convert category labels into
axis ticks; `direction='horizontal'` puts those labels on the vertical axis.

## CLI

```sh
python -m gum -d plot                    # kitty display
python -m gum -d latex -o formula.svg
python -m gum -d plot -W 800 -r 2 -o plot.png
python -m gum -d slide -o slide.pdf
python -m gum -d slide -o slide.pptx
cat input.jsx | python -m gum -f svg
```

`-W/--width` and `-H/--height` set pixel dimensions. `-r/--ratio`, `-t/--theme`,
`-b/--background`, and `--text-mode` match the Python render options. Use
`-f/--format` to override a filename's format.
Use `--page 2` to select the second page of a document supplied on stdin.
`python -m gum --help` lists the built-in demos.

See [Gum's reference](https://compendiumlabs.ai/gum/docs), `gum/dem.py`, and
`gum.ipynb` for current examples.

## Development

Source builds and development require **Bun 1.4.2 or newer**. From this checkout:

```sh
python -m pip install -e '.[plotting]'
bun install --cwd gum/js --frozen-lockfile
bun run --cwd gum/js typecheck
python -m unittest discover -s test -v
```

The editable install builds the backend automatically. Run
`bun run --cwd gum/js build` after editing backend source.

To work against your current local Gum workspace, install that workspace's
dependencies, then link this adapter to its checked-out packages:

```sh
bun install --cwd /home/doug/mlai/gum-jsx
bun run --cwd gum/js link /home/doug/mlai/gum-jsx
```

Linking updates the adapter's ignored `node_modules` entries and rebuilds its
backend. Run `bun run --cwd gum/js build` after changing the linked Gum sources.
Run `bun install --cwd gum/js --force --frozen-lockfile` to restore registry
dependencies.

Tests cover all demos, math, plotting, text escaping, sizing, themes, binary
formats, pixel orientation, subprocess recovery, concurrent requests, notebook
display, and the CLI. Optional integrations run when their Python packages are
installed.

## Building the Python package

```sh
python -m pip install build
python -m build
```

This creates a source archive and wheel in `dist/`. The wheel build uses Bun to
install the locked registry dependencies in a temporary directory and bundle the
backend. Local dependency links are preserved. Wheels contain the JavaScript
bundle, font assets, and third-party notices; they need only Node.js at runtime.
Source archives contain the TypeScript sources and Bun lockfile, so building a
wheel from source requires Bun.
