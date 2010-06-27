import numpy

OMEGA_MIN, OMEGA_MAX = -1500.0, 1500.0
OMEGA_STEP = 50.0

from itertools import imap
from verispeak.api import _model_factory, _enroll, processor


def calc_rates(omega, target, impostor):
    def calc_rate(scores):
        if scores.size > 0:
            positives = numpy.where(scores > omega)[0].size
            return float(positives) / scores.size
        else:
            return 0
    return (omega, calc_rate(target), calc_rate(impostor))

def accumulate_scores(score_func, samples):
    return numpy.fromiter(imap(score_func, samples), dtype=float, count=len(samples))

def make_llr_estimator(null_estimator, alt_estimator):
    return lambda features: null_estimator.loglikelihood(features.features)\
            - alt_estimator.loglikelihood(features.features)

def calc_dets_for_estimator(llr_estimator, target_samples, impostor_samples):
    scores = target_scores, impostor_scores =\
            accumulate_scores(llr_estimator, target_samples),\
            accumulate_scores(llr_estimator, impostor_samples)

    def yield_dets():
        for omega in numpy.arange(OMEGA_MIN, OMEGA_MAX, OMEGA_STEP):
            yield calc_rates(omega, target_scores, impostor_scores)
    
    return numpy.array(list(yield_dets())), scores

def calc_dets(enroll_samples, target_samples, impostor_samples,
        ubm_model, model_classname='CournapeauGMM', model_parameters={}):

    model = _model_factory(model_classname, model_parameters)
    from verispeak.features.feature_vectors import concatenate_vectors
    enroll_features = concatenate_vectors(enroll_samples)
    trained_model = _enroll(enroll_features, model)
   
    score_func = make_llr_estimator(trained_model, ubm_model)
    return calc_dets_for_estimator(score_func, target_samples, impostor_samples)
    
def calc_dets_simple(enroll_samples_filenames, target_samples_filenames, impostor_samples_filenames,
        ubm_model_filename, model_classname='CournapeauGMM', model_parameters={}, processor=processor):
    enroll_samples = map(processor.process, enroll_samples_filenames)
    target_samples = map(processor.process, target_samples_filenames)
    impostor_samples = map(processor.process, impostor_samples_filenames)
    
    from verispeak.util import load_pickled_file
    ubm_model = load_pickled_file(ubm_model_filename)
    return calc_dets(enroll_samples, target_samples, impostor_samples, ubm_model,
            model_classname, model_parameters)

