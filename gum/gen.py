# Python constructors for the current Gum element catalog.
from .utl import Var, Con, Element as BaseElement, Group as BaseGroup, DisplayMixin


class VarGen:
    def __getattr__(self, name):
        return lambda value: Var(name, value)


class ConGen:
    def __getattr__(self, name):
        return Con(name)

    def __call__(self, value):
        return Con(value)


V = VarGen()
C = ConGen()
px = C.px
em = C.em


class Element(BaseElement):
    tag = 'Element'

    def __init__(self, tag=None, unary=True, **args):
        super().__init__(tag or self.tag, unary, **args)


class Group(BaseGroup):
    tag = 'Group'

    def __init__(self, *children, tag=None, **args):
        super().__init__(*children, tag=tag or self.tag, **args)


class DataElement(Element):
    # Geometry is a property in current Gum, not an element child.
    def __init__(self, points=None, **args):
        if points is not None:
            args['points'] = points
        super().__init__(**args)


# Layout and document elements.
class Svg(Group):
    tag = 'Svg'


class Box(Group):
    tag = 'Box'


class Frame(Group):
    tag = 'Frame'


class HStack(Group):
    tag = 'HStack'


class VStack(Group):
    tag = 'VStack'


class Grid(Group):
    tag = 'Grid'


class Overlay(Group):
    tag = 'Overlay'


class TransformBox(Group):
    tag = 'TransformBox'


class Rotate(Group):
    tag = 'Rotate'


class Attach(Group):
    tag = 'Attach'


class Text(Group):
    tag = 'Text'


class Span(Group):
    tag = 'Span'


class TextStack(Group):
    tag = 'TextStack'


class TextRow(Group):
    tag = 'TextRow'


class TextCol(Group):
    tag = 'TextCol'


class TextGrid(Group):
    tag = 'TextGrid'


class TextBox(Group):
    tag = 'TextBox'


class TextFrame(Group):
    tag = 'TextFrame'


class TextFigure(Group):
    tag = 'TextFigure'


class TitleBox(Group):
    tag = 'TitleBox'


class TitleFrame(Group):
    tag = 'TitleFrame'


class Bullets(Group):
    tag = 'Bullets'


class Slide(Group):
    tag = 'Slide'



# Shapes and marks.
class Spacer(Element):
    tag = 'Spacer'


class Rect(Element):
    tag = 'Rect'


class RoundedRect(Element):
    tag = 'RoundedRect'


class Square(Element):
    tag = 'Square'


class Circle(Element):
    tag = 'Circle'


class Ellipse(Element):
    tag = 'Ellipse'


class Dot(Element):
    tag = 'Dot'


class Path(Element):
    tag = 'Path'


class Line(Element):
    tag = 'Line'


class UnitLine(Element):
    tag = 'UnitLine'


class HLine(Element):
    tag = 'HLine'


class VLine(Element):
    tag = 'VLine'


class Segments(Element):
    tag = 'Segments'


class Arc(Element):
    tag = 'Arc'


class Fill(Element):
    tag = 'Fill'


class HFill(Element):
    tag = 'HFill'


class VFill(Element):
    tag = 'VFill'


class ArrowHead(Element):
    tag = 'ArrowHead'


class Ray(Element):
    tag = 'Ray'


class PngImage(Element):
    tag = 'PngImage'


class GeoMap(Element):
    tag = 'GeoMap'



# Point-based geometry.
class Polyline(DataElement):
    tag = 'Polyline'


class Polygon(DataElement):
    tag = 'Polygon'


class Triangle(DataElement):
    tag = 'Triangle'


class Spline(DataElement):
    tag = 'Spline'


class RoundedLine(DataElement):
    tag = 'RoundedLine'


class Arrow(DataElement):
    tag = 'Arrow'



# Graph and plot elements.
class Graph(Group):
    tag = 'Graph'


class Plot(Group):
    tag = 'Plot'


class BarPlot(Group):
    tag = 'BarPlot'


class Points(Group):
    tag = 'Points'


class SymPoints(Group):
    tag = 'SymPoints'


class Field(Group):
    tag = 'Field'


class Network(Group):
    tag = 'Network'


class Node(Group):
    tag = 'Node'


class Axis(Group):
    tag = 'Axis'


class HAxis(Group):
    tag = 'HAxis'


class VAxis(Group):
    tag = 'VAxis'


class Scale(Group):
    tag = 'Scale'


class HScale(Group):
    tag = 'HScale'


class VScale(Group):
    tag = 'VScale'


class Label(Group):
    tag = 'Label'


class HLabel(Group):
    tag = 'HLabel'


class VLabel(Group):
    tag = 'VLabel'


class Labels(Group):
    tag = 'Labels'


class HLabels(Group):
    tag = 'HLabels'


class VLabels(Group):
    tag = 'VLabels'


class Mesh(Group):
    tag = 'Mesh'


class HMesh(Group):
    tag = 'HMesh'


class VMesh(Group):
    tag = 'VMesh'


class Mesh2D(Group):
    tag = 'Mesh2D'


class Legend(Group):
    tag = 'Legend'


class LegendItem(Group):
    tag = 'LegendItem'


class OuterLabel(Group):
    tag = 'OuterLabel'



# Symbolic curves and bars.
class SymLine(Element):
    tag = 'SymLine'


class SymSpline(Element):
    tag = 'SymSpline'


class SymArrow(Element):
    tag = 'SymArrow'


class SymPoly(Element):
    tag = 'SymPoly'


class SymFill(Element):
    tag = 'SymFill'


class SymField(Element):
    tag = 'SymField'


class Bar(Element):
    tag = 'Bar'


class VBar(Element):
    tag = 'VBar'


class HBar(Element):
    tag = 'HBar'


class Bars(Element):
    tag = 'Bars'


class VBars(Element):
    tag = 'VBars'


class HBars(Element):
    tag = 'HBars'


class Edge(Element):
    tag = 'Edge'



# Math elements.
class MathSpan(Group):
    tag = 'MathSpan'


class MathSymbol(Group):
    tag = 'MathSymbol'


class MathRow(Group):
    tag = 'MathRow'


class MathText(Group):
    tag = 'MathText'


class MathChoice(Group):
    tag = 'MathChoice'


class MathCol(Group):
    tag = 'MathCol'


class MathBox(Group):
    tag = 'MathBox'


class Latex(Group):
    tag = 'Latex'


class Tex(Group):
    tag = 'Tex'


class MathOp(Group):
    tag = 'MathOp'


class SupSub(Group):
    tag = 'SupSub'


class Frac(Group):
    tag = 'Frac'


class Sqrt(Group):
    tag = 'Sqrt'


class Bracket(Group):
    tag = 'Bracket'


class TextMode(Group):
    tag = 'TextMode'


class MathArray(Group):
    tag = 'MathArray'


class Accent(Group):
    tag = 'Accent'


class Underline(Group):
    tag = 'Underline'


class Overline(Group):
    tag = 'Overline'


class MathStretch(Group):
    tag = 'MathStretch'


class HorizBrace(Group):
    tag = 'HorizBrace'


class XArrow(Group):
    tag = 'XArrow'


class Phantom(Group):
    tag = 'Phantom'


class Smash(Group):
    tag = 'Smash'


class Lap(Group):
    tag = 'Lap'


class Enclose(Group):
    tag = 'Enclose'


class RaiseBox(Group):
    tag = 'RaiseBox'


class VCenter(Group):
    tag = 'VCenter'


class Pmb(Group):
    tag = 'Pmb'



# Math spacing.
class MathSpacer(Element):
    tag = 'MathSpacer'


class MathRule(Element):
    tag = 'MathRule'


# Retain aliases whose current equivalents have the same meaning.
Shape = Polygon
SymShape = SymPoly
Equation = Latex
Rectangle = Rect
CoordLine = Polyline
TextLine = Text


class Bold(Span):
    def __init__(self, *children, **args):
        super().__init__(*children, **{'font_weight': C.bold, **args})


class Italic(Span):
    def __init__(self, *children, **args):
        super().__init__(*children, **{'font_style': 'italic', **args})


class Stack(Group):
    def __init__(self, *children, direction='vertical', **args):
        if direction not in ('horizontal', 'vertical'):
            raise ValueError('Stack direction must be horizontal or vertical')
        tag = 'HStack' if direction == 'horizontal' else 'VStack'
        super().__init__(*children, tag=tag, **args)


class ArrowSpline(Arrow):
    def __init__(self, points=None, **args):
        super().__init__(points, **{'curve': True, **args})


# DataFrame variables use stable identifiers independent of display labels.
def ensure_var(var, name=None):
    import numpy as np
    import pandas as pd
    if isinstance(var, (np.ndarray, list, tuple)):
        var = pd.Series(var)
    elif isinstance(var, pd.Index):
        var = var.to_series()
    if isinstance(var, pd.Series):
        var = Var.from_series(var, name=name)
    elif not isinstance(var, Var):
        raise ValueError(f'Unsupported type: {type(var)}')
    return var

class GumData:
    def __init__(self, data, index=None):
        self.index = ensure_var(index, name='index')
        self._data = [ ensure_var(v, name=f'value_{i}') for i, v in enumerate(data) ]

    @classmethod
    def from_frame(cls, frame):
        data = [frame.iloc[:, i] for i in range(len(frame.columns))]
        return cls(data, index=frame.index)

    @classmethod
    def from_series(cls, series):
        return cls([ series ], index=series.index)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, name):
        return self._data[name]

    def __setitem__(self, name, value):
        self._data[name] = ensure_var(value, name=name)

    def define(self):
        return '\n'.join([ v.define() for v in [ self.index, *self._data ] ])

##
## top level
##

class Gum(DisplayMixin):
    def __init__(self, cont, vars=None):
        if vars is None:
            vars = []
        elif not isinstance(vars, (tuple, list)):
            vars = [ vars ]
        self.vars = vars
        self.content = cont

    def __str__(self):
        header = '\n'.join([ v.define() for v in self.vars ])
        if len(header) > 0:
            return f'{header}\n\nreturn {self.content}'
        else:
            return str(self.content)
