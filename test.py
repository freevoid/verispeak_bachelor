#!/usr/bin/env python2.5
import sys

try:
    fc = sys.argv[1]
except:
    fc = 'MFCCFeatures'

try:
    sc = sys.argv[2]
except:
    sc = 'DTWScore'

from src import test, wave
test.printout_test(wave.listdir('sounds'), features_class=fc, scoring_class=sc)

