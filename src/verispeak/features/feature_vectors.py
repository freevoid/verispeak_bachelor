from verispeak.base import SerializableObject
from mfcc import mfcc_framed
import numpy as np

__all__ = ['FeatureVectors', 'MFCCFeatureVectors',
        'concatenate_vectors', 'common_normalization']

def mean_normalization(feature_vectors):
    vectors = feature_vectors.features
    mean = sum(vectors)/len(vectors)
    feature_vectors.features = vectors - mean
    return feature_vectors

def delta_mfcc(feature_vectors):
    assert isinstance(feature_vectors, MFCCFeatureVectors)
    mfcc_array = feature_vectors.features.tolist()
    for i, mfcc_vector in enumerate(mfcc_array[2:-2]):
        i += 2
        next_vector = mfcc_array[i+2]
        prev_vector = mfcc_array[i-2]
        delta_c = []
        for ic, c in enumerate(mfcc_vector):
            delta_c.append(next_vector[ic] - prev_vector[ic])
        mfcc_array[i] = np.append(mfcc_vector, delta_c)

    feature_vectors.features = np.array(mfcc_array[2:-2])
    return feature_vectors

common_normalization = (mean_normalization, delta_mfcc)

class FeatureVectors(SerializableObject):
    def __iter__(self):
        return iter(self.features)
    
    def __len__(self):
        return len(self.features)

    def serialize(self):
        frames = self.frames
        self.frames = None
        import cPickle
        dump = cPickle.dumps(self, -1)
        self.frames = frames
        return dump

class MFCCFeatureVectors(FeatureVectors):
    frames = None
    features = None

    def __init__(self, framed_speech=None, nceps=13):
        super(MFCCFeatureVectors, self).__init__()

        # in cases where we want to manually construct object
        # we wan't to be able to create `empty` instances
        if framed_speech is None:
            return

        self.frames = framed_speech
        self.features = mfcc_framed(framed_speech.frames, fs=framed_speech.wave.samplerate, nceps=nceps)[0]
        #NOTE delete first coefficient from feature set
        self.features = self.features[:, 1:]

    def __unicode__(self):
        return u"%s, %d feature frames" % (self.frames, len(self.features),)

def concatenate_vectors(feature_vectors_list):
    return np.concatenate([f.features for f in feature_vectors_list if len(f.features) > 0])

