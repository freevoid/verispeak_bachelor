import logging
from itertools import imap
from importlib import import_module

implementations = ['reference', 'cournapeau_gmm']#, 'cournapeau2_gmm']

for mod in implementations:
    try:
        m = import_module("%s.%s" % (__name__, mod))
        locals().update(dict(
            (x.__name__, x) for x in imap(m.__getattribute__, m.__all__)
            ))
    except BaseException, e:
        logging.warning("Cannot import GMM implementation %s:", mod, exc_info=1)

try:
    from plotting import GMMPlotter
except RuntimeError: # no display
    pass
except ImportError: # no matplotlib or such
    pass

