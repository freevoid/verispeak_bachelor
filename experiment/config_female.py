from helpers import relative_path_generator

relpath = relative_path_generator(__file__)

WAV_DIR = relpath('data/wav_female')
FEATURES_DIR = relpath('data/features_female')
DETS_DIR = relpath('data/dets/female')
PLOT_DIR = relpath('data/plots/female')
MODELS_DIR = relpath('data/models/female')
ENROLL_COUNT = 15
