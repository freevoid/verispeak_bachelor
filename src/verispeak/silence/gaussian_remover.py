import numpy as np

from verispeak.features.segmentaxis import segment_axis

def remove_silence(wave, empirical_silence_time=50, window_length_ms=10, w=0.5):
    fs = wave.samplerate
    edge = int(empirical_silence_time * fs / 1000.0)
    window = int(window_length_ms * fs / 1000.0)
    slice = wave.waveform[:edge]
    n = len(slice)
    mu = slice.mean()
    triple_sigma = 3*np.sqrt(np.square(slice - mu).sum() / n)
    print mu, triple_sigma

    def is_voiced_sample(sample):
        return abs(sample - mu) > triple_sigma
    def is_voiced(window):
        #return abs(window.mean() - mu) > triple_sigma
        wlen = len(window)
        voiced_len = sum(int(is_voiced_sample(sample)) for sample in window)
        return voiced_len > w*wlen

    frames = segment_axis(wave.waveform, window)
    wave._data = np.array([frame for frame in frames if is_voiced(frame)]).flatten(), fs
    return wave

from functools import partial
remove_silence_noisy_env = partial(remove_silence, w=0.3)

if __name__=='__main__':
    from optparse import OptionParser
    op = OptionParser()
    op.add_option("-o", "", action="store", dest="outfile", help="Name of output file")
    op.add_option("-i", "", action="store", dest="infile", help="Name of input file")
    op.add_option("-w", "", action="store", dest="weight", default=0.4)
    op.add_option("-s", "", action="store", dest="empirical_silence_time", default=50, help="Empirical silence time in ms at the beginning of record")
    options, args = op.parse_args()
    window_length_ms = 10

    print "Unsilencing `%s`" % options.infile
    from core.wave import Wave
    w = Wave(options.infile)
    w = remove_silence(w, int(options.empirical_silence_time), window_length_ms, w=float(options.weight))
    w.write_file(options.outfile)

