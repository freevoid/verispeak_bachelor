#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
import sys

kwargs = {}
try:
    features_class = sys.argv[1]
    if features_class == 'gmm':
        action = 'gmm'
    else:
        action = 'timeseries'
except:
    features_class = 'MFCCFeaturesSlice'
    action = 'timeseries'

try:
    scoring_class = sys.argv[2]
except:
    scoring_class = 'DTWScore'


from src.core import test
f=getattr(test, action)
f(**locals())

