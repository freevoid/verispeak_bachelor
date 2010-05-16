from gmm import *

try:
    from plotting import GMMPlotter
except RuntimeError: # no display
    pass
except ImportError: # no matplotlib or such
    pass

