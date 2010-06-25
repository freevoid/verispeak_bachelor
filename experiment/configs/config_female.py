from helpers import relative_path_generator

_relpath = relative_path_generator(__file__)
relpath = lambda path: _relpath('../' + path)


WAV_DIR = relpath('data/wav_female')
FEATURES_DIR = relpath('data/features_female')
DETS_DIR = relpath('data/dets/female')
PLOT_DIR = relpath('data/plots/female')
MODELS_DIR = relpath('data/models/female')
ENROLL_COUNT = 15
