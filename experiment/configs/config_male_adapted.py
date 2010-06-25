from config_male import *

MODELS_DIR = relpath('data/models/male_adapted')
DETS_DIR = relpath('data/dets/male_adapted')
PLOT_DIR = relpath('data/plots/male_adapted')

import verispeak
MODEL_FACTORY=lambda: verispeak.gmm.AdaptedCournapeauGMM(K=32)
UBM_PATH = relpath('./data/ubm/ubm32.gmm')
