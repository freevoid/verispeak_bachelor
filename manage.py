#!/usr/bin/env python
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

elif action == 'gmmcmp':
    try:
        gmm_file = sys.argv[2]
        try:
            features_class = sys.argv[3]
        except:
            features_class = DEFAULT_EXTRACTOR
    except:
        gmm_file = 'инсценировать.gmm'
        features_class = DEFAULT_EXTRACTOR
elif action == 'gmm_retrain':
    try:
        gmm_file = sys.argv[2]
        try:
            features_class = sys.argv[3]
        except:
            features_class = DEFAULT_EXTRACTOR
    except:
        gmm_file = 'инсценировать.gmm'
        features_class = DEFAULT_EXTRACTOR
else:
    action = 'gmmcmp'

from verispeak import test
f=getattr(test, action)
#print "Calling action %s with attributes: %s" % (action, locals())
f(**locals())

