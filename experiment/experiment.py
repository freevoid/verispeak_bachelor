#!/usr/bin/env python
import os
import sys
import logging

import config
import prepare
import calc_data
import plot_dets
import calc_experiment_wise

def experiment_map(experiment_config, func):
    fname = func.__name__
    for cfg in experiment_config:
        logging.info("Performing %s with config %s", fname, cfg.make_postfix())
        func(cfg)

def prepare_experiment(experiment_config):
    for cfg in experiment_config:
        logging.info("Preparing models to '%s'", cfg.MODELS_DIR)
        prepare.main(cfg)

def calc_data_experiment(experiment_config):
    for cfg in experiment_config:
        logging.info("Preparing data to '%s'", cfg.DETS_DIR)
        calc_data.calc_overall(cfg)
        plot_dets.main(cfg)

def all_in_one(config):
    prepare.main(config)
    calc_data.main(config)
    calc_data.calc_overall_configured(config)
    plot_dets.main(config)

def main(exp_config):
    experiment_map(exp_config, all_in_one)

if __name__=='__main__':
    config_dotted_name = sys.argv[1]

    # read base config
    cfg = config.ExperimentConfig.read_config(config_dotted_name)
    #main(cfg)
    #prepare_experiment(cfg)

