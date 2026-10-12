## utils

import json
import inspect
import math
import re
from collections import defaultdict

from .gum import evaluate, display

##
## mixins
##

class AlgMixin:
    def __add__(self, other):
        return Con(f'({self})+({stringify(other)})')

    def __radd__(self, other):
        return Con(f'({stringify(other)})+({self})')

    def __sub__(self, other):
        return Con(f'({self})-({stringify(other)})')

    def __rsub__(self, other):
        return Con(f'({stringify(other)})-({self})')

    def __mul__(self, other):
        return Con(f'({self})*({stringify(other)})')

    def __rmul__(self, other):
        return Con(f'({stringify(other)})*({self})')

    def __truediv__(self, other):
        return Con(f'({self})/({stringify(other)})')

    def __rtruediv__(self, other):
        return Con(f'({stringify(other)})/({self})')

    def __pow__(self, other):
        return Con(f'({self})**({stringify(other)})')

    def __rpow__(self, other):
        return Con(f'({stringify(other)})**({self})')

    def __mod__(self, other):
        return Con(f'({self})%({stringify(other)})')

    def __rmod__(self, other):
        return Con(f'({stringify(other)})%({self})')

    def __eq__(self, other):
        return Con(f'({self})==({stringify(other)})')

    def __req__(self, other):
        return Con(f'({stringify(other)})==({self})')

    def __ne__(self, other):
        return Con(f'({self})!=({stringify(other)})')

    def __rne__(self, other):
        return Con(f'({stringify(other)})!=({self})')

    def __gt__(self, other):
        return Con(f'({self})>({stringify(other)})')

    def __rgt__(self, other):
        return Con(f'({stringify(other)})>({self})')

    def __ge__(self, other):
        return Con(f'({self})>=({stringify(other)})')

    def __rge__(self, other):
        return Con(f'({stringify(other)})>=({self})')

    def __lt__(self, other):
        return Con(f'({self})<({stringify(other)})')

    def __rlt__(self, other):
        return Con(f'({stringify(other)})<({self})')

    def __le__(self, other):
        return Con(f'({self})<=({stringify(other)})')

    def __rle__(self, other):
        return Con(f'({stringify(other)})<=({self})')

    def __and__(self, other):
        return Con(f'({self})&&({stringify(other)})')

    def __rand__(self, other):
        return Con(f'({stringify(other)})&&({self})')

    def __or__(self, other):
        return Con(f'({self})||({stringify(other)})')

    def __ror__(self, other):
        return Con(f'({stringify(other)})||({self})')

    def __xor__(self, other):
        return Con(f'({self})^({stringify(other)})')

    def __rxor__(self, other):
        return Con(f'({stringify(other)})^({self})')

    def __neg__(self):
        return Con(f'-({self})')

    def __pos__(self):
        return Con(f'+({self})')

    def __getitem__(self, key):
        return Con(f'({self})[{stringify(key)}]')

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return self[name]

    def __bool__(self):
        raise TypeError('Symbolic expressions have no Python truth value')

    def __call__(self, *args):
        return Con(f'({self})({", ".join([ stringify(a) for a in args ])})')

##
## values
##

class Var(AlgMixin):
    def __init__(self, name, value):
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', name):
            raise ValueError('Variable names must be JavaScript identifiers')
        self.name = name
        self.value = value

    @classmethod
    def from_series(cls, s, name=None):
        return cls(name if name is not None else s.name, s)

    def __str__(self):
        return self.name

    def define(self):
        return f'const {self.name} = {stringify(self.value)}'

class Con(AlgMixin):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Fun:
    def __init__(self, func):
        sig = inspect.signature(func)
        self.args = [ Con(p.name) for p in sig.parameters.values() ]
        self.ret = func(*self.args)

    def __str__(self):
        args = ', '.join([ str(a) for a in self.args ])
        return f'({args}) => ({stringify(self.ret)})'

##
## core elements
##

def is_notebook():
    try:
        from IPython import get_ipython
        return 'IPKernelApp' in get_ipython().config
    except:
        return False

class DisplayMixin:
    def _ipython_display_(self):
        if is_notebook():
            from IPython.display import display_svg
            svg = evaluate(self)
            display_svg(svg, raw=True)
        else:
            print() # make it on a new line
            display(self)

class Element(DisplayMixin):
    def __init__(self, tag, unary, **args):
        self.tag = tag
        self.unary = unary
        self.args = args

    def inner(self):
        return ''

    def __str__(self):
        args = convert_args(self.args)
        if self.unary:
            return f'<{self.tag} {args} />'
        else:
            inner = self.inner()
            return f'<{self.tag} {args}>\n{inner}\n</{self.tag}>'

class Group(Element):
    def __init__(self, *children, tag='Group', **args):
        unary = len(children) == 0
        super().__init__(tag, unary, **args)
        self.children = children

    def inner(self):
        return '\n'.join([ indented(convert_child(c)) for c in self.children ])

##
## converters
##

def snake_case(s):
    return s.rstrip('_').replace('_', '-')

def stringify(value):
    # convert functions to Functions
    if callable(value) and not isinstance(value, AlgMixin):
        value = Fun(value)

    # convert numeric values to lists
    if not isinstance(value, AlgMixin) and hasattr(value, 'tolist'):
        value = value.tolist()

    # short circuit for gum values
    if isinstance(value, (Var, Con, Fun, Element)):
        return str(value)

    # handle basic json types
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, float):
        if math.isnan(value):
            return 'NaN'
        if math.isinf(value):
            return 'Infinity' if value > 0 else '-Infinity'
        return repr(value)
    elif isinstance(value, str):
        return json.dumps(value) # handles escaping
    elif isinstance(value, (list, tuple)):
        return f'[{", ".join([ stringify(v) for v in value ])}]'
    elif isinstance(value, dict):
        pairs = [f'{json.dumps(str(k))}: {stringify(v)}' for k, v in value.items()]
        return '{' + ', '.join(pairs) + '}'
    else:
        raise ValueError(f'Unsupported type: {type(value)}')

def convert_argval(v):
    return '{' + stringify(v) + '}'

COLOR_KEYS = {'fill', 'stroke', 'color', 'background', 'border_color'}
def convert_color(v):
    if isinstance(v, tuple):
        nums = ', '.join(str(c) for c in v)
        name = 'rgba' if len(v) == 4 else 'rgb'
        return f'{name}({nums})'
    else:
        return v

def convert_args(opts):
    opts1 = {
        k: convert_color(v) if k in COLOR_KEYS else v
        for k, v in opts.items() if v is not None
    }
    return ' '.join([
        f'{snake_case(k)}={convert_argval(v)}' for k, v in opts1.items()
    ])

def convert_child(value):
    enc = stringify(value)
    if isinstance(value, Element):
        return enc
    else:
        return f'{{{enc}}}'

def indented(text, n=2):
    tab = n * ' '
    lines = text.split('\n')
    return '\n'.join([ f'{tab}{line}' for line in lines ])

##
## arg handlers
##

def prefix_split(pres, attr):
    # handle single prefix
    if not isinstance(pres, (tuple, list)):
        pres = [ pres ]
        squeeze = True
    else:
        squeeze = False

    # collect attributes
    pattr = defaultdict(dict)
    attr0 = {}
    for key, val in attr.items():
        for p in pres:
            if key.startswith(f'{p}_'):
                k1 = key[len(p)+1:]
                pattr[p][k1] = val
                break
        else:
            attr0[key] = val

    # return attributes
    attr1 = pattr[pres[0]] if squeeze else [ pattr[p] for p in pres ]
    return attr1, attr0
