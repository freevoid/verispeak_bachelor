from itertools import imap
import logging
import numpy

from verispeak.processors import CommonMFCCStack
from verispeak.features import concatenate_vectors
import verispeak.gmm
processor = CommonMFCCStack()

__all__ = ['score', 'enroll']

class EnrollmentError(Exception): pass

def filenames_to_features(filenames, processor=processor):
    '''
    Shortcut function to convert iterable of filenames to unite numpy array.

    @var filenames: iterable of filepaths to sound files that we need to
        convert (*.wav, etc.)
    @var processor: verispeak.speech_processing.FileToFeaturesStack subclass
        instance (or something that has attribute 'process' that takes filename
        as an argument and returns verispeak.features.feature_vectors.FeatureVectors instance
    @retval: numpy.ndarray instance representing all the features
    '''
    return concatenate_vectors(imap(processor.process, filenames))

def score(null_model, alternative_model, filenames):
    '''
    Computes a so-called Log Likelihood Ratio between likelihoods of two
    hypothesises.
    
    Null hypothesis: speech in filenames was spoken by claimed speaker,
        represented by null_model;
    Alternative hypothethis: speech in filenames was spoken NOT BY claimed
        speaker. To estimate latter likelihood we use alternative_model (UBM).

    @var filenames: iterable of filepaths to sound files, that we need to score
    @retval: float, representing LLR between two hypothesises
    '''
    test_samples = filenames_to_features(filenames)
    null_likelihood = null_model.loglikelihood(test_samples)
    alt_likelihood = alternative_model.loglikelihood(test_samples)

    return null_likelihood - alt_likelihood

def _enroll(sample_features, model, retries=5, train_parameters={}):
    retry = 0
    while retry < retries:
        try:
            model.train(sample_features, **train_parameters)
        except KeyboardInterrupt:
            # if manually interrupted -- just return model as is at current moment
            return model
        except:
            logging.info("Error occured while training GMM, retrying..")
            retry += 1
        else:
            return model

    raise EnrollmentError("Failing after %d unsuccessfull retries to train a model." % retry)

def _model_factory(model_classname, model_parameters={}):
    model_cls = getattr(verispeak.gmm, model_classname)
    return model_cls(**model_parameters)

def enroll(sample_files, model_classname='CournapeauGMM', model_parameters={}, retries=5):
    '''
    High-level function to train a speaker model from sample sound files.
    
    @var model_classname: string, representing one of available model classes
        (currently only Gaussian Mixture Models from verispeak.gmm)
    @var model_parameters: dict-like object that will be passed to model
        constructor
    @var retries: int, number of retries of training phase (it can be failed
        because of small amount of train data and bad initialization try
        (initialization of initial model parameters involves random picking).
    @retval: verispeak.gmm.base.Codebook instance, trained from provided sample
        files
    '''
    gmm = _model_factory(model_classname, model_parameters)
    enroll_samples = filenames_to_features(sample_files)
    return _enroll(enroll_samples, gmm, retries=retries)

def retrain(model, sample_files, retries=5):
    retrain_samples = filenames_to_features(sample_files)
    return _enroll(retrain_samples, model, retries=retries, train_parameters={'no_init': True})

