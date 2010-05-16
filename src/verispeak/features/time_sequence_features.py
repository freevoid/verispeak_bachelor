from ..base import TimeSequence
from mfcc import mfcc
import numpy as np

class TimeSequenceFeatures(TimeSequence):
    def __init__(self, wave):
        super(TimeSequenceFeatures, self).__init__()
        self.wave = wave
        self.flatten_features = None

    def __len__(self):
        return len(self.features)

class MFCCFeaturesSlice(TimeSequenceFeatures):
    def __init__(self, wave, nslice=0, window_length_ms=20):
        super(MFCCFeaturesSlice, self).__init__(wave)
        nwin = window_length_ms*wave.samplerate/1000.0
        overlap = int(nwin*0.375)
        nwin = int(nwin)
        self.features = mfcc(wave.waveform, fs=wave.samplerate, nwin=nwin, over=overlap)[0]
        self.flatten_features = np.array([cc[nslice] for cc in self.features])

class PeakFeatures(TimeSequenceFeatures):
    def __init__(self, wave, window_length_ms=50):
        super(PeakFeatures, self).__init__(wave)
        mfcc = MFCCFeaturesSlice(wave).__flatten__()

        from ..peak_picking import find_peaks
        peaks = find_peaks(mfcc, int(mfcc.size*0.2))
        #print peaks
        self.peaks = peaks

        peaks_array = self.make_array(peaks, mfcc.size)
        self.features = peaks_array

        self.flatten_features = list(self.features)

    @staticmethod
    def make_array(peaks, n):
        peaks_array = np.zeros(n)
        for i in peaks:
            peaks_array[i] = 10.0
        return peaks_array

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

