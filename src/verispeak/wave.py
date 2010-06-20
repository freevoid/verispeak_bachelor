import os.path
from scikits import audiolab

from verispeak import misc
from verispeak import util
from verispeak.base import Object

WAV_EXT = '.wav'
SUPPORTED_FORMATS = (WAV_EXT,)

def listdir(dirpath):
    import os
    import os.path
    import itertools
    return itertools.ifilter(lambda filename: os.path.isfile(filename) and os.path.splitext(filename)[1] in SUPPORTED_FORMATS,
            (os.path.join(os.path.abspath(dirpath), filename) for filename in os.listdir(dirpath)))

def read_file(filename):
    from os import path
    ext = path.splitext(filename)[1].lower()
    if ext == WAV_EXT:
        amplitudes_array, sample_frequency, fmt = audiolab.wavread(filename)
    else:
        raise NotImplementedError("Format '%s' not supported. Supported formats are: %s" % (ext, ', '.join(SUPPORTED_FORMATS)))
    return amplitudes_array, sample_frequency

def write_file(wave, filename):
    from os import path
    ext = path.splitext(filename)[1].lower()
    if ext == WAV_EXT:
        return audiolab.wavwrite(wave.waveform, filename, fs=wave.samplerate)
    else:
        raise NotImplementedError("Format '%s' not supported. Supported formats are: %s" % (ext, ', '.join(SUPPORTED_FORMATS)))

def read_dir(dirpath):
    files = listdir(dirpath)
    return map(Wave, files)

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

    def resample(self, new_fs=16000):
        self._data = misc.resample(self.waveform, self.samplerate, new_fs), new_fs
        return self

    def plot_amp(self, **matplotlib_kwargs):
        import plotting
        return plotting.plot_amp(*self._data, **matplotlib_kwargs)

    def unify_size(self, other):
        """
        Resamples two waveforms so that they with equal in size.

        >>> w1 = Wave('test1.wav')
        >>> w2 = Wave('test2.wav')
        >>> len(w1)
        13020
        """

        if isinstance(other, Wave):
            return zip(*misc.coerce(self._data, other._data))[0]
        elif util.isiterable(other):
            if len(other) == 2:
                return zip(*misc.coerce(self._data, other))[0]
            else:
                return misc.coerce_no_sf(self.waveform, other)
        else:
            return NotImplemented

    def play(self, speed_scale=None):
        if speed_scale is not None:
            fs = self.samplerate*speed_scale
        else:
            fs = self.samplerate
        audiolab.play(self.waveform, fs)

    def __len__(self):
        return len(self.waveform)

    def __unicode__(self):
        return self.filename

    read_file = staticmethod(read_file)
    write_file = write_file

def _test():
    import doctest
    doctest.testmod()

if __name__=='__main__':
    _test()

