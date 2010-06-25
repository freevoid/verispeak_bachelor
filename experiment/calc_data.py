#!/usr/bin/env python

from verispeak.benchmarking import make_llr_estimator, calc_dets_for_estimator
from verispeak.util import load_pickled_file

from micromake import walk_on_files

import numpy as np
import os
import logging
import glob

def preload_features(features_dir):
    features = {}
    for id in os.listdir(features_dir):
        subdir = os.path.join(features_dir, id)
        features[id] = [load_pickled_file(features_file) for features_file in walk_on_files(subdir)]
    return features

def find_err(det):
    for omega, target, impostor in det:
        target = 1 - target
        if impostor <= target:
            if impostor == 0.0:
                return 0.0
            else:
                return target
    return None

def calc_dets(models_dir, features_dir, ubm_file, target_offset=10, max_per_impostor=10):
    ubm = load_pickled_file(ubm_file)
    
    logging.info("Preloading feature vectors..")
    features_dict = preload_features(features_dir)

    for model_file in glob.glob(os.path.join(models_dir, '*.gmm')):
        logging.info("Calculating DETS for model in `%s`.." % model_file)
        
        id = os.path.splitext(os.path.basename(model_file))[0]
        model = load_pickled_file(model_file)
        estimator = make_llr_estimator(model, ubm)

        target_features = features_dict[id][target_offset:]

        impostor_features = sum((features[:max_per_impostor]
            for (impostor_id, features) in features_dict.iteritems() if impostor_id != id), [])

        dets, scores = calc_dets_for_estimator(estimator, target_features, impostor_features)
        yield id, dets, scores

def calc_and_write_dets(models_dir, features_dir, ubm_file, out_dir, scores_dir, target_offset=10, delim=' '):
    dets_iterator = calc_dets(models_dir, features_dir, ubm_file, target_offset)

    for id, dets, scores in dets_iterator:
        outfile = os.path.join(out_dir, id + '.txt')
        np.savetxt(outfile, dets)

        target_scores_file = os.path.join(scores_dir,  id + '_target_scores.txt')
        impostor_scores_file = os.path.join(scores_dir, id + '_impostor_scores.txt')
        target, impostor = scores
        np.savetxt(target_scores_file, target)
        np.savetxt(impostor_scores_file, impostor)

        logging.info("DETS for %s saved to `%s`", id, outfile)

def calc_overall(cfg):
    
    count = 0
    det_files = glob.iglob(os.path.join(cfg.DETS_DIR, "*.txt"))
    omega0, t, i = np.loadtxt(det_files.next(), unpack=True)
    n = len(omega0)
    total_t = t
    total_i = i
    for det_file in det_files:
        omega, t, i = np.loadtxt(det_file, unpack=True)
        assert all(omega == omega0)
        total_t += t
        total_i += i

    t = total_t / n
    i = total_i / n

    print find_err(zip(*(omega, t, i)))
    logging.info("Saving average DET curve in '%s'" % cfg.DETS_DIR)
    np.savetxt(os.path.join(cfg.DETS_DIR, 'overall.txt'), np.array([omega, t, i]))

def configured_calc_and_write_dets(cfg):
    return calc_and_write_dets(cfg.MODELS_DIR, cfg.FEATURES_DIR,
            cfg.UBM_PATH, cfg.DETS_DIR, cfg.SCORES_DIR, cfg.ENROLL_COUNT)

main = configured_calc_and_write_dets

if __name__=='__main__':
    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]
    from config import Config
    cfg = Config.read_config(config_dotted_name)

    configured_calc_and_write_dets(cfg)
    logging.info("DETS successfully calculated and saved.")

