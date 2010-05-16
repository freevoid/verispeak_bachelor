from segmentaxis import segment_axis

from scipy.signal import hamming, lfilter

from ..base import Object

def preemp(input, p):
    """Pre-emphasis filter."""
    return lfilter([1., -p], 1, input)

def frame_signal(input, nwin=256, over=None):
    # MFCC parameters: taken from auditory toolbox
    over = over if over is not None else nwin - 160
    # Pre-emphasis factor (to take into account the -6dB/octave rolloff of the
    # radiation at the lips level)
    prefac = 0.97
    extract = preemp(input, prefac)
    w = hamming(nwin, sym=0)
    framed = segment_axis(extract, nwin, over) * w
    return framed

class FramedSpeech(Object):
    def __init__(self, wave, window_length_ms=15, window_overlap=0.5):
        nwin = window_length_ms*wave.samplerate/1000.0
        overlap = int(nwin*window_overlap)
        nwin = int(nwin)

        self.frames = frame_signal(wave.waveform, nwin=nwin, over=overlap)
        self.wave = wave

