import cPickle
import collections

from delegate import Delegate

__all__=['Delegate', 'isiterable', 'load_pickled_file']

def isiterable(x):
    return isinstance(x, collections.Iterable)

def load_pickled_file(f):
    unpickled = cPickle.load(f)
    if type(unpickled) in (list, tuple) and hasattr(unpickled[0], 'deserialize'):
        return unpickled[0].deserialize(unpickled)
    else:
        return unpickled

