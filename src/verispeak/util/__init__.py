import cPickle
import collections

from delegate import Delegate

__all__=['Delegate', 'isiterable', 'load_pickled_file']

def isiterable(x):
    return isinstance(x, collections.Iterable)

def check_output_interface(target):
    return all([hasattr(target, 'close'),
        hasattr(target, 'write')])

def check_input_interface(target):
    return all([hasattr(target, 'close'),
        hasattr(target, 'read'),
        hasattr(target, 'readlines')])

def check_file_interface(target, mode):
    res = False
    if 'r' in mode:
        res = check_input_interface(target)
    if 'w' in mode:
        res = res and check_output_interface(target)
    return res

def solve_file_or_filename(file_or_filename, mode):
    if check_file_interface(file_or_filename, mode):
        return file_or_filename
    elif isinstance(file_or_filename, basestring):
        return open(file_or_filename, mode)

def load_pickled_file(file_or_filename):
    f = solve_file_or_filename(file_or_filename, 'rb')
    unpickled = cPickle.load(f)
    if type(unpickled) in (list, tuple) and hasattr(unpickled[0], 'deserialize'):
        return unpickled[0].deserialize(unpickled)
    else:
        return unpickled

