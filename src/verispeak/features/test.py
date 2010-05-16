import numpy as np

from scipy.io import loadmat
try:
    from scipy.signal import lfilter, hamming
except:
    pass
    
from scipy.fftpack import fft
from scipy.fftpack.realtransforms import dct

from segmentaxis import segment_axis

print "Done"
