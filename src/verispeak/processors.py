from speech_processing import TemplatedFileToFeaturesStack
from wave import Wave
from silence import gaussian_remover
from features import framing, feature_vectors
import exceptions
import numpy as np

import itertools
def remove_zero_offset(wave):
    offset = itertools.dropwhile(lambda (i, a): a==0.0, enumerate(wave.waveform)).next()[0]
    wave.set_data(wave.waveform[offset:], wave.samplerate)
    return wave

def remove_zero_frames(framed_speech, treshhold=1e-5):
    framed_speech.frames = np.array([frame for frame in framed_speech.frames if np.abs(frame).sum() > treshhold])
    return framed_speech

def check_min_length(wave, min_timelength_ms=500):
    tl = wave.timelength
    if min_timelength_ms is not None and tl < min_timelength_ms:
        raise exceptions.InsufficientUtteranceLength(tl, min_timelength_ms)

    return wave

def check_max_length(wave, max_timelength_ms=3500):
    tl = wave.timelength
    if max_timelength_ms is not None and tl > max_timelength_ms:
        raise exceptions.TooBigUtteranceLength(tl, max_timelength_ms)

    return wave

class CommonStack(TemplatedFileToFeaturesStack):
    raw_norm = (Wave.resample, remove_zero_offset, gaussian_remover.remove_silence_noisy_env, check_min_length)
    frame_norm = (remove_zero_frames,)

class CommonMFCCStack(CommonStack):
    post_norm = feature_vectors.common_normalization
    framer = framing.FramedSpeech
    extractor = feature_vectors.MFCCFeatureVectors

