# gum visualization

from itertools import cycle

from .gen import C, GumData, Gum, Points, SymLine, SymSpline, Plot, BarPlot
from .utl import prefix_split

##
## themes
##

DEFAULT_BASE = {
    'aspect': 2,
    'margin': C.em(0.75),
}

DEFAULT_PLOT = {
    **DEFAULT_BASE,
    'grid': True,
    'line_stroke_width': C.px(2),
}

DEFAULT_BARS = {
    **DEFAULT_BASE,
    'stroke': C.none,
    'border_radius': {'t': C.px(4)},
    'fill': C.blue,
}

COLORS = [
    C.blue,
    C.green,
    C.red,
    C.yellow,
    C.purple,
    '#fb8c00',
]

##
## plotting interface
##

def test_data(which='brown', T=500, L=3, N=20, K1=1, K2=10):
    import numpy as np
    import pandas as pd
    if which == 'trig':
        df = pd.DataFrame({ 'theta': np.linspace(0, 2 * np.pi, 100) })
        return df.assign(sin=np.sin(df.theta), cos=np.cos(df.theta)).set_index('theta')
    elif which == 'brown':
        return pd.DataFrame({
            f'stock_{i}': np.random.randn(T).cumsum() / np.sqrt(T) for i in range(L)
        })
    elif which == 'bars':
        codes = np.random.randint(K1, K2, N)
        return pd.Series({ chr(65+c): v for c, v in enumerate(codes) }, name='value')
    else:
        raise ValueError(f'Unknown test data: {which}')

def ensure_series(data):
    import numpy as np
    import pandas as pd
    if isinstance(data, (np.ndarray, list, tuple, dict)):
        data = pd.Series(data, name='value')
    if not isinstance(data, pd.Series):
        raise ValueError(f'Unsupported type: {type(data)}')
    return data

def ensure_frame(data):
    import numpy as np
    import pandas as pd
    if isinstance(data, (np.ndarray, list, tuple)):
        data = pd.DataFrame({ 'value': data })
    elif isinstance(data, dict):
        data = pd.DataFrame({ k: ensure_series(v) for k, v in data.items() })
    elif isinstance(data, pd.Series):
        data = data.to_frame()
    if not isinstance(data, pd.DataFrame):
        raise ValueError(f'Unsupported type: {type(data)}')
    return data

def lines(frame, spline=False, **kwargs):
    # collect arguments
    args = { **DEFAULT_PLOT, **kwargs }
    line_args, plot_args = prefix_split('line', args)

    # convert to dataframe
    frame = ensure_frame(frame)
    data = GumData.from_frame(frame)

    # get maker class
    Maker = SymSpline if spline else SymLine

    # data plotters
    lines = [
        Maker(xvals=data.index, yvals=v, **{'stroke': c, **line_args})
        for v, c in zip(data, cycle(COLORS))
    ]

    # generate svg code
    plot = Plot(*lines, **plot_args)
    return Gum(plot, vars=data)

def points(frame, shape=None, point_size=None, **kwargs):
    # collect arguments
    args = {**DEFAULT_BASE, 'grid': True, **kwargs}
    point_args, plot_args = prefix_split('point', args)

    # convert to dataframe
    frame = ensure_frame(frame)
    data = GumData.from_frame(frame)

    # Marker size is a display length independent of the data range.
    if point_size is None:
        point_size = C.px(6)

    # data plotters
    points = [
        Points(
            points=C.zip(data.index, v),
            shape=shape,
            point_size=point_size,
            **{'fill': c, **point_args}
        )
        for v, c in zip(data, cycle(COLORS))
    ]

    # generate svg code
    plot = Plot(*points, **plot_args)
    return Gum(plot, vars=data)

def bars(series, **kwargs):
    # collect arguments
    args = { **DEFAULT_BARS, **kwargs }

    # convert to series
    series = ensure_series(series)
    data = GumData.from_series(series)

    # Category labels are axis ticks; bar geometry uses numeric positions.
    values = next(iter(data))
    positions = list(range(len(series)))
    ticks = [(i, str(label)) for i, label in enumerate(series.index)]
    axis = 'yticks' if args.get('direction') == 'horizontal' else 'xticks'
    args.setdefault(axis, ticks)
    plot = BarPlot(values=values, positions=positions, **args)
    return Gum(plot, vars=data)
