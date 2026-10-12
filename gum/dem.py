# Runnable examples using current Gum sizing, geometry, and math APIs.
from .gen import C, V, px, em
from . import gen as G


def linspace(start, stop, num):
    delta = (stop - start) / (num - 1)
    return [start + i * delta for i in range(num)]


def sine_plot(*children, **args):
    # Curves sample their own domain before the Plot computes its layout.
    defaults = dict(xlim=(0, 2*C.pi), ylim=(-1.5, 1.5), aspect=2, grid=True)
    return G.Plot(*children, **{**defaults, **args})


def sine_curve(**args):
    return G.SymLine(**{
        'fy': C.sin, 'xlim': (0, 2*C.pi), 'stroke': C.blue,
        'stroke_width': px(2), **args,
    })


def demo_gum():
    return G.Frame(G.Text('GUM', font_size=em(3)), padding=em(1), border_radius=px(8))


def demo_element():
    return G.Polygon([(0.5, 0.1), (0.9, 0.9), (0.1, 0.9)], fill=C.blue)


def demo_group():
    return G.Group(
        G.Rotate(G.Rect(fill=C.blue, width=px(120), height=px(80)),
                 angle=15, pos=(0.3, 0.3)),
        G.Ellipse(pos=(0.7, 0.7), width=0.2, height=0.2, fill=C.red),
    )


def demo_box():
    return G.Frame(G.Text('hello!'), padding=em(1), border_radius=px(8), border_width=px(2))


def demo_stack():
    return G.VStack(
        G.RoundedRect(height=px(100), fill=C.blue),
        G.HStack(
            G.Square(width=px(100), border_radius=px(8), fill=C.red),
            G.Square(width=px(100), border_radius=px(8), fill=C.green),
            gap=em(1),
        ),
        gap=em(1),
    )


def demo_grid():
    return G.Grid(
        *[
            G.Frame(
                G.Rotate(
                    G.Arrow(from_=(0.15, 0.5), to=(0.85, 0.5), head_size=px(10),
                            width=px(80), height=px(80)),
                    angle=angle, width=px(80), height=px(80),
                ),
                padding=em(0.5), border_radius=px(6),
            )
            for angle in range(0, 360, 40)
        ],
        columns=3, gap=em(0.5),
    )


def demo_points():
    return G.Plot(
        G.Points(points=[(0, 0.5), (0.5, 0), (-0.5, 0), (0, -0.5)],
                 point_size=px(10), fill=C.red),
        G.SymLine(fy=C.sin, xlim=(-1, 1), stroke=C.blue),
        xlim=(-1, 1), ylim=(-1, 1), grid=True, aspect=1,
        xlabel='time (seconds)', ylabel='space (meters)', title='Spacetime Vibes',
    )


def demo_rect():
    return G.Group(G.Rect(pos=(0.25, 0.5), width=0.2, height=0.4, fill=C.blue))


def demo_ellipse():
    return G.Group(
        G.Ellipse(pos=(0.3, 0.2), width=0.4, height=0.2, fill=C.blue),
        G.Ellipse(pos=(0.6, 0.6), width=0.4, height=0.5, fill=C.green),
    )


def demo_line():
    return G.Group(
        G.Line(from_=(0.2, 0.2), to=(0.8, 0.8), stroke=C.blue),
        G.Polyline([(0.3, 0.3), (0.3, 0.7), (0.7, 0.7), (0.7, 0.3)], stroke=C.red),
    )


def demo_shape():
    return G.Group(
        G.Polygon([(0.5, 0.2), (0.8, 0.8), (0.2, 0.8)], fill=C.blue, stroke=C.none),
        G.Polygon([(0.3, 0.3), (0.3, 0.7), (0.7, 0.7), (0.7, 0.3)],
                  fill=C.green, stroke=C.none, opacity=0.5),
    )


def demo_spline():
    points = [(0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75), (0.5, 0.5)]
    return G.Group(
        G.Spline(points, closed=True, stroke=C.blue, fill=C.lightgray),
        G.Polygon(points, stroke=C.red, fill=C.none),
        G.Points(points=points, point_size=px(6), fill=C.red),
    )


def demo_text():
    return G.TextFrame(
        G.Text(
            'Hello World! Mix text with ', G.Span('bold', font_weight=C.bold),
            ' and ', G.Span('italic', font_style='italic'),
            ' spans, or inline math: ', G.Tex(r'\alpha + \beta'),
        ),
        width=px(400), padding=em(1), border_radius=px(8),
    )


def demo_titleframe():
    return G.TitleFrame(
        G.Grid(
            *[G.TextBox(label, padding=em(0.8), border_width=px(1))
              for label in ['Apple', 'Pear', 'Peach', 'Plum', 'Lime', 'Mango']],
            columns=3, gap=em(0.5),
        ),
        title='Fruits', padding=em(1), border_radius=px(8),
    )


def demo_slide():
    return G.Slide(
        G.Text('The sine wave repeats every two pi radians.'),
        sine_plot(sine_curve(), height=px(220)),
        G.Text('Its range is -1 to 1.'),
        title='The Art of the Sine Wave', width=px(800), height=px(450),
    )


def demo_latex():
    return G.VStack(
        G.Frame(G.Latex(r'\int_0^{\infty} \exp(-x^2)\,dx = \frac{\sqrt{\pi}}{2}'),
                padding=em(1), border_width=px(2)),
        G.Frame(G.Latex(r'\sin^2(\theta) + \cos^2(\theta) = 1'),
                padding=em(1), border_width=px(2)),
        gap=em(1),
    )


def demo_sympoints():
    return sine_plot(
        sine_curve(),
        G.SymPoints(
            fy=C.sin, xlim=(0, 2*C.pi), samples=11, point_size=px(12),
            shape=lambda point, index: G.Rotate(
                G.RoundedRect(fill=C.red), angle=-C.r2d*C.atan(C.cos(point.x))),
        ),
    )


def demo_symline():
    return sine_plot(
        sine_curve(stroke=C.red),
        sine_curve(fy=lambda x: C.sin(x) + 0.2*C.sin(5*x)),
    )


def demo_symshape():
    radius = lambda t: 1 - 0.3*C.cos(2.5*t)**2
    return G.Graph(
        G.SymPoly(fx=lambda t: radius(t)*C.sin(t), fy=lambda t: radius(t)*C.cos(t),
                  tlim=(0, 2*C.pi), samples=200, fill=C.blue),
        aspect=1, padding=0.1,
    )


def demo_symspline():
    decay = lambda x: C.exp(-x/2)*C.sin(3*x)
    domain = dict(fy=decay, xlim=(0, 2*C.pi))
    return sine_plot(
        G.SymLine(**domain, samples=200, opacity=0.25),
        G.SymSpline(**domain, samples=10, stroke=C.blue, stroke_width=px(2)),
        G.SymPoints(**domain, samples=10, point_size=px(6), fill=C.red),
    )


def demo_symfill():
    decay = lambda x: C.exp(-0.1*x)*C.sin(x)
    return G.Graph(
        G.SymFill(upper=decay, lower=0, xlim=(0, 6*C.pi),
                  fill=C.blue, opacity=0.5, samples=250),
        G.SymLine(fy=decay, xlim=(0, 6*C.pi), samples=250),
        xlim=(0, 6*C.pi), ylim=(-1, 1), aspect=2,
    )


def demo_graph():
    return G.Graph(
        G.SymPoints(
            fy=C.sin, xlim=(0, 2*C.pi), samples=30, point_size=px(10),
            shape=lambda point, index: G.Rotate(G.Square(fill=C.blue), angle=C.r2d*point.x),
        ),
        ylim=(-1.5, 1.5), padding=0.1, aspect=2,
    )


def demo_plot():
    ticks = [(x*C.pi, f'{x:.2g} π') for x in linspace(0, 2, 6)]
    return sine_plot(
        sine_curve(fy=lambda x: -C.sin(x)), xticks=ticks,
        xlabel='phase', ylabel='amplitude', title='Inverted Sine Wave',
        xaxis_tick_side='outer', grid_stroke_dasharray=[px(3), px(3)],
    )


def demo_axis():
    ticks = [(i/4, label) for i, label in enumerate(['A', 'B', 'C', 'D', 'E'])]
    return G.Box(G.HAxis(lim=(0, 1), ticks=ticks, width=px(400), height=px(50)), padding=em(1))


def demo_barplot():
    return G.BarPlot(
        values=[3, 8.5, 6.5], xticks=[(0, 'A'), (1, 'B'), (2, 'C')],
        styles=[{'fill': C.red}, {'fill': C.blue}, {'fill': C.green}],
        ylim=(0, 10), yticks=6, border_radius={'t': px(6)},
        title='Example BarPlot', xlabel='Category', ylabel='Value', aspect=2,
    )


def demo_node():
    return G.Network(
        G.Node('Hello', id='hello', pos=(0.25, 0.25)),
        G.Node('World!', id='world', pos=(0.75, 0.75)),
        G.Edge(start='hello', end='world'), xlim=(0, 1), ylim=(0, 1),
    )


def demo_edge():
    return G.Network(
        G.Node('Hello', id='hello', pos=(0.25, 0.25)),
        G.Node('World!', id='world', pos=(0.75, 0.75)),
        G.Edge(start='hello', end='world', start_head=True, head_fill=C.red),
        xlim=(0, 1), ylim=(0, 1),
    )


def demo_network():
    return G.Network(
        G.Node('Hello', id='hello', pos=(0.2, 0.5)),
        G.Node('A wrapped label for a network node', id='test',
               pos=(0.75, 0.75), width=px(140)),
        G.Node(G.Ellipse(width=px(90), height=px(60), fill=C.blue),
               id='ball', pos=(0.75, 0.25)),
        G.Edge(start='hello', end='test'),
        G.Edge(start='hello', end='ball', start_side='bottom', curve=True),
        xlim=(0, 1), ylim=(0, 1), aspect=1.5,
    )


def demo_math():
    return sine_plot(sine_curve(fy=lambda x: C.exp(C.sin(x))), ylim=(0, 3))


def demo_arrays():
    return G.Plot(
        *[G.Text(str(i), pos=(i, i)) for i in range(1, 6)],
        xlim=(0, 6), ylim=(0, 6), xticks=7, yticks=7,
    )


def demo_colors():
    color = V.colors(C.palette(C.blue, C.red, (-1, 1)))
    plot = sine_plot(
        sine_curve(fy=lambda x: -C.sin(x)),
        G.SymPoints(
            fy=lambda x: -C.sin(x), xlim=(0, 2*C.pi), samples=21,
            point_size=lambda point, index: px(6 + 6*C.abs(point.y)),
            shape=lambda point, index: G.Circle(fill=C.colors(point.y)),
        ),
        xlabel='phase', ylabel='amplitude', title='Colored Sine Wave',
    )
    return G.Gum(plot, vars=[color])


DEMOS = {
    name[len('demo_'):]: value
    for name, value in list(globals().items()) if name.startswith('demo_')
}


def demo(name):
    return DEMOS[name]()
