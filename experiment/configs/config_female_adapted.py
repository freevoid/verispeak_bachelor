from config_female import *

MODELS_DIR = relpath('data/models/female_adapted')
DETS_DIR = relpath('data/dets/female_adapted')
PLOT_DIR = relpath('data/plots/female_adapted')

import verispeak
MODEL_FACTORY=lambda: verispeak.gmm.AdaptedCournapeauGMM(K=32)
UBM_PATH = relpath('./data/ubm/ubm32.gmm')

