#!/usr/bin/env python

'''
This is a shortcut for all neccessary actions:
    * Prepare features and models;
    * Calculate DET data for each target speaker in test set;
    * Plot DET plots and save them as pictures in given format.
'''

import sys
config_dotted_name = sys.argv[1]

from config import Config
cfg = Config.read_config(config_dotted_name)

import logging
logging.basicConfig(level=logging.DEBUG)
steps = ('prepare', 'calc_data', 'plot_dets')

for step in steps:
    cb_module = __import__(step)
    entry_point = getattr(cb_module, 'main')
    entry_point(cfg)

