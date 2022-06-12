from ansi.colour import fg
from ansi.colour.base import Graphic
from ansi.colour.fx import reset
import builtins
import numpy

log_debug = False

def path(s):
    return fg.brown, repr(s), reset

def primitive_color(obj, nested):
    s = str(obj)
    t = type(obj)
    if issubclass(t, bytes) or (issubclass(t, str) and nested):
        skip = 2
        if issubclass(t, str):
            skip = 1
            s = repr(s)
        return fg.brown, s[:skip], fg.yellow, s[skip:-1], fg.brown, s[-1], reset
    if issubclass(t, bool):
        if obj:
            return fg.green, s, reset
        return fg.red, s, reset
    if issubclass(t, int) or issubclass(t, numpy.integer):
        return fg.cyan, s, reset
    if issubclass(t, float) or issubclass(t, numpy.floating):
        return fg.green, s, reset
    if issubclass(t, Graphic):
        return (s,)
    if issubclass(t, list) or issubclass(t, tuple):
        start, end = '(', ')'
        if issubclass(t, list):
            start, end = '[', ']'
        return fg.gray, start, (str(fg.gray) + ', ').join(map(color, obj)), fg.gray, end
    return s, reset

def color(obj, nested=True):
    return ''.join(map(str, primitive_color(obj, nested)))

def debug(*args, **kwargs):
    if log_debug:
        print(*args, prefix=(fg.red, '[DEBUG]:', reset))

def print(*args, prefix=None, **kwargs):
    if log_debug:
        if prefix:
            args = prefix + args            
        else:
            args = [fg.blue, '[INFO]:', reset] + list(args)
    pargs = []
    prev = ''
    for arg in args:
        if issubclass(type(arg), Graphic):
            prev += str(arg)
            continue
        if prev:
            pargs.append(prev + str(arg) + str(reset))
            prev = ''
        else:
            pargs.append(color(arg, nested=False))
    builtins.print(*pargs, **kwargs)