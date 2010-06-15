# -*- coding: utf-8 -*-
import wave
import features as features_module
import processors as speech_processors
from util import load_pickled_file
import gmm as gmm_module, feature_suite

def gmm(gmm_class, phrase, features_class='CommonMFCCStack', model_order=8, retries=5, train_args={}, **kwargs):
    features_class = getattr(speech_processors, features_class)
    gmm_class = getattr(gmm_module, gmm_class)
    fs1 = feature_suite.FeaturesSuite(phrase, speech_processor=features_class())
    fs1.read_dir('sounds')
    print 'Got %d samples' % len(fs1.samples)
    m = gmm_class(K=model_order)
    retry = 0
    while retry < retries:
        try:
            print m.train(fs1.flat, **train_args)
        except KeyboardInterrupt:
            break
        except:
            print "Error occured, retrying.."
            retry += 1
        else:
            break
    filename = phrase + '.gmm'
    m.dump_to_file(filename)
    print "GMM Codebook saved to file: '%s'" % filename

def gmmcmp(gmm_file, features_class='CommonMFCCStack', **kwargs):
    features_class = getattr(speech_processors, features_class)
    gmm = load_pickled_file(open(gmm_file))
    print "Got gmm:", gmm
    assert(hasattr(gmm, 'loglikelihood'))
    
    processor = features_class()
    features_pool = map(processor.process, wave.listdir('sounds'))
 
    d = dict((gmm.loglikelihood(features_vectors.features),(features_vectors.frames.wave.filename)) for features_vectors in features_pool)

    print "%s: %s" % (gmm_file, repr(gmm))
    for target_score in sorted(d, reverse=True):
        filename = d[target_score]
        print "%15.5f %s" % (target_score, filename)

def gmm_retrain(gmm_file, features_class='CommonMFCCStack', phrase=None, train_args={}, **kwargs):
    if phrase is None:
        import os
        phrase = os.path.basename(gmm_file).rsplit('.', 1)[0]
    features_class = getattr(speech_processors, features_class)
    gmm = load_pickled_file(open(gmm_file))

    fs1 = feature_suite.FeaturesSuite(phrase, speech_processor=features_class())
    fs1.read_dir('sounds')

    print 'Got %d samples' % len(fs1.samples)
    try:
        print gmm.train(fs1.flat, no_init=True, **train_args)
    except KeyboardInterrupt:
        pass
    gmm.dump_to_file(gmm_file)
    print "Retrained GMM Codebook saved to file: '%s'" % gmm_file

