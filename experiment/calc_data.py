#!/usr/bin/env python

from verispeak.benchmarking import make_llr_estimator, calc_dets_for_estimator
from verispeak.util import load_pickled_file

from micromake import walk_on_files

import numpy as np
import os
import logging
import glob
import itertools

from util import save_det_to_txt, load_det_from_txt

def preload_features(features_dir):
    features = {}
    for id in os.listdir(features_dir):
        subdir = os.path.join(features_dir, id)
        features[id] = [load_pickled_file(features_file) for features_file in walk_on_files(subdir)]
    return features

def canonize_det(det):
    if det.shape[0] == 3 and det.shape != (3,3):
        det = det.T
    return det

def find_eer(det):
    det = canonize_det(det)
    for omega, target, impostor in det:
        target = 1 - target
        if impostor <= target:
            if impostor == 0.0:
                return 0.0
            else:
                return target
    return None

def calc_dets(models_dir, features_dir, ubm_file, target_offset=10, max_per_impostor=None):
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

        save_det_to_txt(outfile, dets)

        target_scores_file = os.path.join(scores_dir,  id + '_target_scores.txt')
        impostor_scores_file = os.path.join(scores_dir, id + '_impostor_scores.txt')
        target, impostor = scores
        np.savetxt(target_scores_file, target)
        np.savetxt(impostor_scores_file, impostor)

        logging.info("DETS for %s saved to `%s`", id, outfile)

def calc_overall_det(dets_dir):
    count = 1
    det_files = glob.iglob(os.path.join(dets_dir,  "???.txt"))
    omega0, t, i = load_det_from_txt(det_files.next())
    n = len(omega0)
    total_t = t
    total_i = i
    for det_file in det_files:
        omega, t, i = load_det_from_txt(det_file)
        assert all(omega == omega0)
        total_t += t
        total_i += i
        count += 1

    t = total_t / count
    i = total_i / count

    return np.array([omega, t, i]).transpose()

def calc_and_save_overall(dets_dir):
    det = calc_overall_det(dets_dir)
    #print find_eer(det)
    logging.info("Saving average DET curve in '%s'" % dets_dir)
    save_det_to_txt(os.path.join(dets_dir, 'overall.txt'), det)
    return det

def calc_overall_configured(cfg):
    return calc_and_save_overall(cfg.DETS_DIR)

def obrain_overall(dets_dir):
    overall_filename = os.path.join(dets_dir, 'overall.txt')
    if os.access(overall_filename, os.F_OK):
        overall = load_det_from_txt(overall_filename)
    else:
        overall = calc_and_save_overall(dets_dir)
    return overall

def calc_eer(dets_dir):
    overall = obrain_overall(dets_dir)
    print overall.shape
    return find_eer(overall)

def _calc_delta(det):
    det = canonize_det(det)
    a = b = None
    for omega, t, i in det:
        if t < 1.0 and a is None:
            a = omega
            if b is not None: break
        if i < 1e-10 and b is None:
            b = omega
            if a is not None: break

    if a is None or b is None:
        raise ValueError("Can't find start points of FA and FP curves")
    return a, b, b - a


def calc_delta(dets_dir):
    overall = obrain_overall(dets_dir)
    return _calc_delta(overall)

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

