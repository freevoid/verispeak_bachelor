#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
import sys

kwargs = {}
action = sys.argv[1]
if action == 'gmm':
    try:
        gmm_class = sys.argv[2]

        try:
            model_order = int(sys.argv[3])
            try:
                phrase = sys.argv[4]
                try:
                    features_class = sys.argv[5]
                except:
                    features_class = 'CommonMFCCStack'
            except:
                phrase = 'инсценировать'
                features_class = 'CommonMFCCStack'
        except:
            phrase = 'инсценировать'
            features_class = 'CommonMFCCStack'
    except:
        phrase = 'инсценировать'
        gmm_class = 'GMM'
        features_class = 'CommonMFCCStack'

elif action == 'timeseries':
    features_class = sys.argv[2]
    try:
        scoring_class = sys.argv[3]
    except:
        scoring_class = 'DTWScore'
elif action == 'gmmcmp':
    try:
        gmm_file = sys.argv[2]

        try:
            features_class = sys.argv[3]
        except:
            features_class = 'CommonMFCCStack'
    except:
        gmm_file = 'инсценировать.gmm'
        features_class = 'CommonMFCCStack'
elif action == 'gmm_retrain':
    try:
        gmm_file = sys.argv[2]

        try:
            features_class = sys.argv[3]
        except:
            features_class = 'CommonMFCCStack'
    except:
        gmm_file = 'инсценировать.gmm'
        features_class = 'CommonMFCCStack'
else:
    features_class = 'MFCCFeaturesSlice'
    action = 'timeseries'

from src.core import test
f=getattr(test, action)
#print "Calling action %s with attributes: %s" % (action, locals())
f(**locals())

