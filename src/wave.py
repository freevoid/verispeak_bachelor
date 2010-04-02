import os.path

import misc
import utils
from base import Object

WAV_EXT = '.wav'
SUPPORTED_FORMATS = (WAV_EXT,)

def listdir(dirpath):
    import os
    import os.path
    import itertools
    return itertools.ifilter(lambda filename: os.path.isfile(filename) and os.path.splitext(filename)[1] in SUPPORTED_FORMATS,
            (os.path.join(os.path.abspath(dirpath), filename) for filename in os.listdir(dirpath)))

def read_file(filename):
    from scikits import audiolab
    from os import path
    ext = path.splitext(filename)[1].lower()
    if ext == WAV_EXT:
        amplitudes_array, sample_frequency, fmt = audiolab.wavread(filename)
    else:
        raise NotImplementedError("Format '%s' not supported. Supported formats are: %s" % (ext, ', '.join(SUPPORTED_FORMATS)))
    return amplitudes_array, sample_frequency

class Wave(Object):
    def __init__(self, filename):
        super(Wave, self).__init__()
        self._data = Wave.read_file(filename)
        self.filepath = os.path.abspath(filename)
        self.filename = os.path.basename(filename)

    @property
    def waveform(self): return self._data[0]

    @property
    def samplerate(self): return self._data[1]

    @property
    def timelength(self):
        return 1000*len(self.waveform) / float(self.samplerate) # in ms

    def plot_amp(self):
        return misc.plot_amp(*self._data)

    def unify_size(self, other):
        if isinstance(other, Wave):
            return zip(*misc.coerce(self._data, other._data))[0]
        elif utils.isiterable(other):
            if len(other) == 2:
                return zip(*misc.coerce(self._data, other))[0]
            else:
                return misc.coerce_no_sf(self.waveform, other)
        else:
            return NotImplemented

    def __len__(self):
        return len(self.waveform)

    def __unicode__(self):
        return self.filename

    read_file = staticmethod(read_file)

