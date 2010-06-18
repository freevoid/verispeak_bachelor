#!/usr/bin/env python

from verispeak.benchmarking import make_llr_estimator, calc_dets_for_estimator
from verispeak.util import load_pickled_file

from micromake import walk_on_files

import os
import logging

def preload_features(features_dir):
    features = {}
    for id in os.listdir(features_dir):
        subdir = os.path.join(features_dir, id)
        features[id] = [load_pickled_file(features_file) for features_file in walk_on_files(subdir)]
    return features

def calc_dets(models_dir, features_dir, ubm_file, target_offset=10):
    ubm = load_pickled_file(ubm_file)
    
    logging.info("Preloading feature vectors..")
    features_dict = preload_features(features_dir)

    for model_file in os.listdir(models_dir):
        logging.info("Calculating DETS for model in `%s`.." % model_file)
        id = os.path.splitext(model_file)[0]
        model_file = os.path.join(models_dir, model_file)
        model = load_pickled_file(model_file)
        estimator = make_llr_estimator(model, ubm)

        target_features = features_dict[id][target_offset:]
        impostor_features = sum((features for (impostor_id, features) in features_dict.iteritems() if impostor_id != id), [])
        
        dets = calc_dets_for_estimator(estimator, target_features, impostor_features)
        yield id, dets

def calc_and_write_dets(models_dir, features_dir, ubm_file, out_dir, target_offset=10, delim=' '):
    dets_iterator = calc_dets(models_dir, features_dir, ubm_file, target_offset)
    for id, dets in dets_iterator:
        outfile = os.path.join(out_dir, id + '.txt')
        f = open(outfile, 'w')
        for omega, (target_y, impostor_y) in dets:
            f.write(delim.join(['%.5f' % omega, '%.18e' % target_y, '%.18e' % impostor_y]))
            f.write('\n')
        f.close()
        logging.info("DETS for %s saved to `%s`", id, outfile)

def configured_calc_and_write_dets(cfg):
    return calc_and_write_dets(cfg.MODELS_DIR, cfg.FEATURES_DIR,
            cfg.UBM_PATH, cfg.DETS_DIR, cfg.ENROLL_COUNT)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)

    import sys
    assert len(sys.argv) == 2
    config_dotted_name = sys.argv[1]
    from config import Config
    cfg = Config.read_config(config_dotted_name)

    configured_calc_and_write_dets(cfg)
    logging.info("DETS successfully calculated and saved.")

