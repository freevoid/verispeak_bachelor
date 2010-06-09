from itertools import imap
import numpy

from verispeak.processors import CommonMFCCStack
import verispeak.gmm
processor = CommonMFCCStack()

__all__ = ['score', 'enroll']

def filenames_to_features(filenames):
    features_list = list(f.features for f in imap(processor.process, filenames))
    ## XXX rude code. Eliminate numpy from here, put concatenation
    ## logic in FeaturesSuite alike class
    return numpy.concatenate(features_list)

def score(null_model, alternative_model, filenames):
    test_samples = filenames_to_features(filenames)
    null_likelihood = null_model.loglikelihood(test_samples)
    alt_likelihood = alternative_model.loglikelihood(test_samples)

    return null_likelihood - alt_likelihood

def enroll(sample_files, model_classname='CournapeauGMM', model_parameters={}):
    model_cls = getattr(verispeak.gmm, model_classname)
    gmm = model_cls(**model_parameters)
    enroll_samples = filenames_to_features(sample_files)
    gmm.train(enroll_samples)
    return gmm

def calc_dets(enroll_samples, target_samples, impostor_samples):
    pass
