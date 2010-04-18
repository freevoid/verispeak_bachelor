from ..base import Object
from mfcc import mfcc
import numpy as np

def mean_normalization(vectors):
    mean = sum(vectors)/len(vectors)
    return vectors - mean 

class MFCCFeatureVectors(Object):
    def __init__(self, wave, window_length_ms=20, normalize_func=mean_normalization):
        super(MFCCFeatureVectors, self).__init__()
        self.wave = wave
        nwin = window_length_ms*wave.samplerate/1000.0
        overlap = int(nwin*0.375)
        nwin = int(nwin)
        self.features = mfcc(wave.waveform, fs=wave.samplerate, nwin=nwin, over=overlap)[0]
        #NOTE delete first coefficient from feature set
        self.features = self.features[:, 1:]
        self.features = normalize_func(self.features)
        self.features = self.calc_delta_mfcc(self.features.tolist())

    def __iter__(self):
        return iter(self.features)

    def __unicode__(self):
        return u"%s, %d feature frames" % (self.wave, len(self.features),)

    def calc_delta_mfcc(self, mfcc_array):
        for i, mfcc_vector in enumerate(mfcc_array[2:-2]):
            i += 2
            next_vector = mfcc_array[i+2]
            prev_vector = mfcc_array[i-2]
            delta_c = []
            for ic, c in enumerate(mfcc_vector):
                delta_c.append(next_vector[ic] - prev_vector[ic])
            mfcc_array[i] = np.append(mfcc_vector, delta_c)
        return np.array(mfcc_array[2:-2])

