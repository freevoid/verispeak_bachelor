from itertools import imap
import logging
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

def enroll(sample_files, model_classname='CournapeauGMM', model_parameters={}, retries=5):
    model_cls = getattr(verispeak.gmm, model_classname)
    enroll_samples = filenames_to_features(sample_files)
    gmm = model_cls(**model_parameters)
    retry = 0
    while retry < retries:
        try:
            gmm.train(enroll_samples)
        except KeyboardInterrupt:
            break
        except:
            logging.info("Error occured while training GMM, retrying..")
            retry += 1
        else:
            break

    return gmm

def calc_dets(enroll_samples, target_samples, impostor_samples):
    pass
