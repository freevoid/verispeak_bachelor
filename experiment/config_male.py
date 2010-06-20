from helpers import relative_path_generator

relpath = relative_path_generator(__file__)

WAV_DIR = relpath('data/wav_male')
FEATURES_DIR = relpath('data/features_male')
MODELS_DIR = relpath('data/models/male')
DETS_DIR = relpath('data/dets/male')
PLOT_DIR = relpath('data/plots/male')
ENROLL_COUNT = 15

