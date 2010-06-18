from helpers import relative_path_generator

relpath = relative_path_generator(__file__)

WAV_DIR = relpath('data/wav_female')
FEATURES_DIR = relpath('data/features_female')
MODELS_DIR = relpath('data/models/female')
