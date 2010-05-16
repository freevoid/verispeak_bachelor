from speech_processing import TemplatedFileToFeaturesStack
from wave import Wave
from silence import gaussian_remover
from features import framing, feature_vectors
import numpy as np

def remove_zero_frames(framed_speech, treshhold=1e-5):
    framed_speech.frames = np.array([frame for frame in framed_speech.frames if np.abs(frame).sum() > treshhold])
    return framed_speech

class CommonStack(TemplatedFileToFeaturesStack):
    raw_norm = (Wave.resample,)# gaussian_remover.remove_silence)
    frame_norm = (remove_zero_frames,)

class CommonMFCCStack(CommonStack):
    post_norm = feature_vectors.common_normalization
    framer = framing.FramedSpeech
    extractor = feature_vectors.MFCCFeatureVectors

