import scoring, wave
import features as features_module

def print_score((pos, (score, o, i))):
    print u"%3d). %30s <-> %30s: %10.4f" % (pos, o.wave.filename, i.wave.filename, score)

def listdir(dirpath):
    import os
    import os.path
    import itertools
    return itertools.ifilter(lambda filename: os.path.isfile(filename) and os.path.splitext(filename)[1] in wave.SUPPORTED_FORMATS,
            (os.path.join(os.path.abspath(dirpath), filename) for filename in os.listdir(dirpath)))

def test(soundfiles, features_class='MFCCFeatures', scoring_class='DTWScore'):
    waves = map(wave.Wave, soundfiles)
    features = map(getattr(features_module, features_class), waves)
    scorings = map(getattr(scoring, scoring_class), features)
    for i, original in enumerate(scorings[:-1]):
        for j in xrange(i+1, len(features)):
            impostor = features[j]
            original.score(impostor)
            yield(original.score(impostor), original.original, impostor)

def printout_test(soundfiles, features_class='MFCCFeatures',
        scoring_class='DTWScore'):
    map(print_score, enumerate(sorted(test(soundfiles,
        features_class=features_class, scoring_class=scoring_class))))

