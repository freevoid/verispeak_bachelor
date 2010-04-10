from mel import mel2hz, hz2mel
__all__  = ['mel2hz', 'hz2mel']

from mfcc import mfcc
__all__ += ['mfcc']

from ..base import ScoreObject, Object
from .. import utils
import numpy as np

class Features(ScoreObject):
    def __init__(self, wave):
        super(Features, self).__init__()
        self.wave = wave
        self.flatten_features = None

    def __len__(self):
        return len(self.features)

class MFCCFeatures(Features):
    def __init__(self, wave, window_length_ms=20):
        super(MFCCFeatures, self).__init__(wave)
        nwin = window_length_ms*wave.samplerate/1000.0
        overlap = int(nwin*0.375)
        nwin = int(nwin)
        self.features = mfcc(wave.waveform, fs=wave.samplerate, nwin=nwin, over=overlap)[0]

    def __flatten__(self):
        self.flatten_features = [np.array(x) for x in zip(*self.features)][:1]
        return self.flatten_features
    #return [np.array([mfcc[12] for mfcc in self.features])]

class PeakFeatures(Features):
    def __init__(self, wave, window_length_ms=50):
        super(PeakFeatures, self).__init__(wave)
        [mfcc] = MFCCFeatures(wave).__flatten__()

        from ..peak_picking import find_peaks
        peaks = find_peaks(mfcc, int(len(mfcc)*0.2))
        #print peaks
        self.peaks = peaks

        peaks_array = self.make_array(peaks, len(mfcc))
        self.features = peaks_array

        self.flatten_features = [self.features]

    @staticmethod
    def make_array(peaks, n):
        peaks_array = np.zeros(n)
        for i in peaks:
            peaks_array[i] = 10.0
        return peaks_array

    def __flatten__(self):
        return [self.features]

    def _force_length(self, length):
        n = len(self)
        if length > n:
            raise AssertionError
        return self.make_array(((length-1)/(n-1))*np.array(self.peaks).astype(np.int32), length)

    def unify_size(self, other):
        n, m = len(self), len(other)
        if n > m:
            return other.unify_size(self)
        assert(m >= n)
        return map(lambda peaks: self.make_array(peaks, m),
                ((((m-1)/(n-1))*np.array(self.peaks)).astype(np.int32),
                np.array(other.peaks, dtype=np.int32)))

class CompositeFeatures(Features):
    def __init__(self, wave, classes=[MFCCFeatures, PeakFeatures]):
        super(CompositeFeatures, self).__init__(wave)
        self.features = [klass(wave) for klass in classes]

    def __len__(self):
        return len(self.features[0])

    def __flatten__(self):
        return [f.__flatten__()[0] for f in self.features]

