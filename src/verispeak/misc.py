import numpy as np

WINDOW_LENGTH = 20 # in ms

RESAMPLE_TYPE = 'sinc_best'

SILENCE_TIME = 50 # ms

def get_timelength(array, sf):
    return 1000*len(array) / float(sf) # in ms

def resample(source, source_sf, target_sf):
    if source_sf != target_sf:
        from scikits import samplerate
        ratio = float(target_sf) / source_sf
        return samplerate.resample(source, ratio, RESAMPLE_TYPE)
    else:
        return source

def detect_noise(source, sf):
    utterance_time = get_timelength(source, sf)
    edge = sf*SILENCE_TIME // 1000
    print 'edge:', edge
    max_level = abs(source[:edge]).max()
    return max_level

def _naive_noise_filter(noise_level):
    def decorator(func):
        def filter(source, samplerate):
            source, samplerate = func(source, samplerate)
            return _naive_noise_filter(source, noise_level), samplerate
        return filter
    return decorator

def naive_noise_filter(source, noise_level):
    for i, amp in enumerate(source):
        if abs(amp) > noise_level:
            break

    for j, amp in enumerate(reversed(source)):
        if abs(amp) > noise_level:
            break
    print "NAIVE_NOISE_FILTER:", noise_level, i, j
    return source[i:len(source)-j]

def normalize(array, sample_frequency):
    # downsample to 16000
    # array, sample_frequency = resample(array, sample_frequency, 16000), 16000

    # remove silence
    noise_level = detect_noise(array, sample_frequency)
    array = naive_noise_filter(array, noise_level)
    
    # TODO reduce noise
    return array, sample_frequency

def coerce(*args):
    (s1, sf1), (s2, sf2) = args
    n, m = len(s1), len(s2)
    if n > m:
        sfnew = m*sf1/float(n)
        snew = resample(s1, sf1, sfnew)
        snew = map(np.float64, snew)
        return (snew, sfnew), (s2, sf2)
    elif n < m:
        sfnew = n*sf2/float(m)
        snew = resample(s2, sf2, sfnew)
        snew = map(np.float64, snew)
        return (s1, sf1), (snew, sfnew)
    return args

def coerce_no_sf(s1, s2):
    s1, s2 = np.array(s1), np.array(s2)
    (ns1, x), (ns2, y) = coerce((s1, 1000), (s2, 1000))
    return ns1, ns2

MIN_TRESHHOLD = 200.0
def calc_treshhold(score_class, sample_features, other_features):
    def get_min_score(features):
        n = len(features)
        smin = MIN_TRESHHOLD
        for i in range(n-1):
            score = score_class(features[i])
            for j in range(i+1, n):
                s = score.score(features[j])
                smin = min(s, smin)
        return smin
    def get_ave_score(features):
        n = len(features)
        score_sum = 0.0
        nscores = 0
        for i in range(n-1):
            score = score_class(features[i])
            for j in range(i+1, n):
                score_sum += score.score(features[j])
                nscores += 1
        return score_sum / nscores

    min_impostor = get_min_score(other_features)
    average_self = get_ave_score(sample_features)
    print "Score limits: %s %s" % (min_impostor, average_self)
    return min(min_impostor, average_self)

