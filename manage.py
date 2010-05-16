#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
import sys

DEFAULT_GMM_CLASS = 'CournapeauDiagonalGMM'
DEFAULT_EXTRACTOR = 'CommonMFCCStack'

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
                    features_class = DEFAULT_EXTRACTOR
            except:
                phrase = 'инсценировать'
                features_class = DEFAULT_EXTRACTOR
        except:
            model_order = 16
            phrase = 'инсценировать'
            features_class = DEFAULT_EXTRACTOR
    except:
        model_order = 16
        phrase = 'инсценировать'
        gmm_class = DEFAULT_GMM_CLASS
        features_class = DEFAULT_EXTRACTOR

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
            gmm_class = sys.argv[3]
            try:
                features_class = sys.argv[4]
            except:
                features_class = DEFAULT_EXTRACTOR
        except:
            features_class = DEFAULT_EXTRACTOR
            gmm_class = DEFAULT_GMM_CLASS
    except:
        gmm_class = DEFAULT_GMM_CLASS
        gmm_file = 'инсценировать.gmm'
        features_class = DEFAULT_EXTRACTOR
elif action == 'gmm_retrain':
    try:
        gmm_file = sys.argv[2]
        try:
            gmm_class = sys.argv[3]
            try:
                features_class = sys.argv[4]
            except:
                features_class = DEFAULT_EXTRACTOR
        except:
            features_class = DEFAULT_EXTRACTOR
            gmm_class = DEFAULT_GMM_CLASS
    except:
        gmm_file = 'инсценировать.gmm'
        gmm_class = DEFAULT_GMM_CLASS
        features_class = DEFAULT_EXTRACTOR
else:
    features_class = 'MFCCFeaturesSlice'
    action = 'timeseries'

from verispeak import test
f=getattr(test, action)
#print "Calling action %s with attributes: %s" % (action, locals())
f(**locals())

