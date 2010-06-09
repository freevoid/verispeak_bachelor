import cPickle

def load_pickled_file(f):
    unpickled = cPickle.load(f)
    if type(unpickled) in (list, tuple) and hasattr(unpickled[0], 'deserialize'):
        return unpickled[0].deserialize(unpickled)
    else:
        return unpickled

