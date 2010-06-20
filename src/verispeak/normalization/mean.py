def raw_mean_normalization(wave, empirical_silence_time=50):
    fs = wave.samplerate
    edge = int(empirical_silence_time * fs / 1000.0)
    mean = wave.waveform[:edge].mean()
    return wave.waveform - mean

