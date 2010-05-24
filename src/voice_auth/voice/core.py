from itertools import imap
import numpy

from verispeak.processors import CommonMFCCStack
processor = CommonMFCCStack()

def load_pickled_file(f):
    import cPickle
    unpickled = cPickle.load(f)
    if type(unpickled) in (list, tuple) and hasattr(unpickled[0], 'deserialize'):
        return unpickled[0].deserialize(unpickled)
    else:
        return unpickled

def score(null_model, alternative_model, filenames):
    features_list = list(f.features for f in imap(processor.process, filenames))
    ## XXX rude code. Eliminate numpy from here, put concatenation
    ## logic in FeaturesSuite alike class
    test_samples = numpy.concatenate(features_list)

    null_likelihood = null_model.loglikelihood(test_samples)
    alt_likelihood = alternative_model.loglikelihood(test_samples)

    print 'LIKELIHOODS:', null_likelihood, alt_likelihood
    return null_likelihood - alt_likelihood

