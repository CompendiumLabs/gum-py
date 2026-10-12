# gum.py

Python adapter for the current Gum libraries in `../gum-jsx`. The backend runs
TypeScript with Bun 1.4.2 or newer; Node alone cannot run the source adapter.

## Setup and checks

```sh
pip install -e '.[plotting]'
python -m gum --install
python -m unittest discover -s test -v
bun run --cwd gum/js typecheck
```

To test the checked-out Gum workspace instead of the pinned registry packages:

```sh
bun install --cwd ../gum-jsx
bun run --cwd gum/js link /absolute/path/to/gum-jsx
```

The link script updates only this adapter's ignored `gum/js/node_modules`
entries. It does not edit package manifests or the Gum workspace. Reinstalling
the backend restores the registry versions. Keep tests in `test/`.

## Architecture

- `gum/gum.py`: lazy, persistent Bun subprocess, serialized JSON/binary requests,
  image conversions, rendering and terminal display.
- `gum/js/pipe.ts`: `create_evaluator` and `layout` from `@gum-jsx/cli`, SVG from
  core, direct fragment PNG/RGBA from `@gum-jsx/png`, PDF/PPTX exporters, and
  `format_image`/`format_pixels` from `@gum-jsx/cli/kitty`.
- `gum/utl.py`: JSX serialization, symbolic variables/constants/functions, and
  Jupyter display. String children and props are escaped JS expressions.
- `gum/gen.py`: current core/math/map constructors, `GumData`, and the
  top-level `Gum` source/preamble container. Match current names without aliases.
- `gum/viz.py`: pandas-friendly `lines`, `points`, and `bars` helpers.
- `gum/dem.py`, `gum.ipynb`: runnable examples.
- `gum/__main__.py`: stdin/demo rendering, file output, and explicit backend install.

Evaluation uses the core, math, maps, and file-loading bindings provided by the
CLI. Layout produces a fragment or a document's pages.
PDF/PPTX export all pages; single-image formats require `page=...` for multi-page
input. PNG rendering consumes a fragment, not an intermediate SVG string.

## API conventions

`evaluate(element)` returns SVG text. `render(element)` returns PNG bytes.
`evaluate(..., output_format='png'|'pixels')` defaults to a PIL image; use
`return_format='bytes'`, or NumPy/Torch for pixels. PDF/PPTX always return bytes.
`display` uses kitty graphics. Imports and JSX construction do not start Bun.

`width`/`height` are independent pixel overrides. No override uses the CLI's
640 × 480 advisory offer, preserving explicit source dimensions and content hug.
Raster `ratio` changes sampling, not layout. Wire sizes are `(width, height)`;
pixel arrays are `(height, width, 4)` uint8 RGBA.

Use `px()`/`em()` for display lengths; bare numbers are relative lengths.
Python snake_case props become kebab-case JSX; a trailing underscore is removed
for Python keywords. Use `samples`, `gap`, `border_radius`, `columns`,
`Line(from_=..., to=...)`, and `Polyline(points)`.

Marker callbacks receive `(point, index)`, with `point.x` and `point.y`.
Sampling domains belong on symbolic curves. Bar data uses numeric positions
plus axis ticks for category labels. Keep DataFrame labels separate from stable
JavaScript variable identifiers.

## Packaging

Keep the Python version aligned with the pinned Gum library release.
Ship backend source, manifests, and lockfile, never `node_modules`. Users install
JavaScript dependencies explicitly with `python -m gum --install`.
