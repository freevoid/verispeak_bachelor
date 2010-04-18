# -*- coding: utf-8 -*-
import scoring, wave
import features as features_module
import gmm as gmm_module, feature_suite

def print_score((pos, (score, o, i))):
    print u"%3d). %30s <-> %30s: %10.4f" % (pos, o.wave.filename, i.wave.filename, score)

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

def timeseries(features_class, scoring_class, **kwargs):
    from src import test, wave
    test.printout_test(wave.listdir('sounds'),
            features_class=features_class,
            scoring_class=scoring_class)

def gmm(features_class, gmm_class, phrase, model_order=8, **kwargs):
    features_class = getattr(features_module, features_class)
    gmm_class = getattr(gmm_module, gmm_class)
    fs1 = feature_suite.FeaturesSuite(phrase, features_class=features_class)
    fs1.read_dir('sounds')
    print 'Got %d samples' % len(fs1.samples)
    m = gmm_class(K=model_order)
    print m.train(fs1.flat)
    filename = phrase + '.gmm'
    m.dump_to_file(filename)
    print "GMM Codebook saved to file: '%s'" % filename

def gmmcmp(features_class, gmm_file, **kwargs):
    features_class = getattr(features_module, features_class)
    import cPickle
    gmm = cPickle.load(open(unicode(gmm_file)))
    
    features_pool = map(features_class, wave.read_dir('sounds'))
 
    d = dict((gmm.loglikelihood(features_vectors.features),(features_vectors.wave.filename)) for features_vectors in features_pool)

    print u"%s: %s" % (gmm_file, repr(gmm))
    for target_score in sorted(d, reverse=True):
        filename = d[target_score]
        print "%15.5f %s" % (target_score, filename)

def gmm_retrain(features_class, gmm_file, phrase=None, **kwargs):
    if phrase is None:
        import os
        phrase = os.path.basename(gmm_file).rsplit('.', 1)[0]
    features_class = getattr(features_module, features_class)
    import cPickle
    gmm = cPickle.load(open(gmm_file))

    fs1 = feature_suite.FeaturesSuite(phrase, features_class=features_class)
    fs1.read_dir('sounds')

    print 'Got %d samples' % len(fs1.samples)
    print gmm.train(fs1.flat, no_init=True)
    gmm.dump_to_file(gmm_file)
    print "Retrained GMM Codebook saved to file: '%s'" % gmm_file

