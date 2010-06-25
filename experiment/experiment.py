#!/usr/bin/env python
import os
import sys
import logging

import config
import prepare
import calc_data
import plot_dets

def make_postfix(cfg):
    return os.path.join(cfg.TRAINING_PROC_NAME, str(cfg.K), str(cfg.ENROLL_COUNT))

def make_factor_dir(cfg, base, postfix=None):
    model_dir = os.path.join(base, postfix if postfix is not None else make_postfix(cfg))
    prepare.force_existence(model_dir)
    return model_dir

def config_generator(experiment_config):
    skeleton_config = experiment_config
    for k in experiment_config.K_RANGE:
        skeleton_config.K = k
        for enroll_count in experiment_config.ENROLL_COUNTS:
            skeleton_config.ENROLL_COUNT = enroll_count
            postfix = make_postfix(experiment_config)
            skeleton_config.MODELS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_MODELS_DIR, postfix)
            skeleton_config.DETS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_DETS_DIR, postfix)
            skeleton_config.PLOT_DIR = make_factor_dir(experiment_config, experiment_config.BASE_PLOT_DIR, postfix)
            skeleton_config.MODEL_FACTORY = None # forces to setup new model factory
            skeleton_config.setup()
        
            yield skeleton_config

def experiment_map(experiment_config, func):
    for cfg in config_generator(experiment_config):
        func(cfg)

def prepare_experiment(experiment_config):
    for cfg in config_generator(experiment_config):
        logging.info("Preparing models to '%s'", cfg.MODELS_DIR)
        prepare.main(cfg)

def calc_data_experiment(experiment_config):
    for cfg in config_generator(experiment_config):
        logging.info("Preparing data to '%s'", cfg.DETS_DIR)
        calc_data.main(cfg)
        plot_dets.main(cfg)

if __name__=='__main__':
    config_dotted_name = sys.argv[1]

    # read base config
    cfg = config.ExperimentConfig.read_config(config_dotted_name)
    #prepare_experiment(cfg)

