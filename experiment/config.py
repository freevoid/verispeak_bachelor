import logging
import os

import verispeak
import util

silence_remover = verispeak.silence.gaussian_remover.remove_silence
from functools import partial
gen_remover = lambda w: partial(silence_remover, w=w)

class SilenceConcernedStack(verispeak.processors.CommonMFCCStack):
    def __init__(self, w):
        self.raw_norm = (verispeak.wave.Wave.resample, gen_remover(w))
        super(SilenceConcernedStack, self).__init__()

class Config(object):
    def __init__(self,
            WAV_DIR='./data/wav',
            MODELS_DIR='./data/models',
            FEATURES_DIR='./data/features',
            DETS_DIR='./data/dets',
            PLOT_DIR='./data/plots',
            ENROLL_COUNT=10,
            UBM_PATH='./data/ubm/ubm16.gmm',
            PLOT_FORMAT='pdf',
            MODEL_FACTORY=None,
            TRAINING_PROC_NAME='EM',
            K=16,
            W=0.8,
            MODEL_CLS='CournapeauGMM',
            TRAINING_PARAMS={'maxiter': 50},
            SCORES_DIR='./data/scores',
            LOGGING_LEVEL=logging.DEBUG,
            **unhandled):
        del unhandled # forget about not supported options
        _locals = locals()
        _locals.pop('self')
        self.__dict__.update(_locals)
        self.setup()

    def setup(self):
        logging.basicConfig(level=self.LOGGING_LEVEL)

        training_proc = getattr(verispeak.training, self.TRAINING_PROC_NAME)
        self.TRAINING_PROC = lambda model, samples: training_proc(model, samples, **self.TRAINING_PARAMS)

        if self.MODEL_FACTORY is None:
            model_cls = getattr(verispeak.gmm, self.MODEL_CLS)
            self.MODEL_FACTORY = lambda: model_cls(K=self.K)

        if self.W is not None:
            self.processor = SilenceConcernedStack(w=self.W)
        else:
            self.processor = verispeak.api.processor

    @classmethod
    def read_config(cls, dotted_name):
        import importlib
        mod = importlib.import_module(dotted_name)
        return cls(**mod.__dict__)

class ExperimentConfig(Config):
    def __init__(self, BASE_MODELS_DIR=None,
            BASE_DETS_DIR=None,
            BASE_PLOT_DIR=None,
            BASE_WAV_DIR=None,
            BASE_FEATURES_DIR=None,
            ENROLL_COUNTS=range(3,21),
            K_RANGE=range(2,33,2),
            W_RANGE=(0.8,),
            **unhandled):
        super(ExperimentConfig, self).__init__(**unhandled)
        del unhandled
        _locals = locals()
        _locals.pop('self')
        self.__dict__.update(_locals)
        self.exp_setup()

    def exp_setup(self):
        super(ExperimentConfig, self).setup()
        if self.BASE_MODELS_DIR is None:
            self.BASE_MODELS_DIR = self.MODELS_DIR
        if self.BASE_DETS_DIR is None:
            self.BASE_DETS_DIR = self.DETS_DIR
        if self.BASE_PLOT_DIR is None:
            self.BASE_PLOT_DIR = self.PLOT_DIR
        if self.BASE_WAV_DIR is None:
            self.BASE_WAV_DIR = self.WAV_DIR
        if self.BASE_FEATURES_DIR is None:
            self.BASE_FEATURES_DIR = self.FEATURES_DIR

    def _copy(self):
        return ExperimentConfig(**self.__dict__)

    def __iter__(self):
        return old_config_generator(self._copy())
 
    def vector(self):
        return (self.K, self.ENROLL_COUNT)#, self.W)

    def make_wave_postfix(self):
        return str(self.W).replace('.', '_')

    def make_postfix(self):
        return os.path.join(self.TRAINING_PROC_NAME, *map(str, self.vector()))

def old_config_generator(experiment_config):
    skeleton_config = experiment_config
    for k in experiment_config.K_RANGE:
        skeleton_config.K = k
        for enroll_count in experiment_config.ENROLL_COUNTS:
            skeleton_config.ENROLL_COUNT = enroll_count
            postfix = experiment_config.make_postfix()
            skeleton_config.MODELS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_MODELS_DIR, postfix)
            skeleton_config.DETS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_DETS_DIR, postfix)
            skeleton_config.PLOT_DIR = make_factor_dir(experiment_config, experiment_config.BASE_PLOT_DIR, postfix)
            skeleton_config.MODEL_FACTORY = None # forces to setup new model factory

            skeleton_config.setup()
            yield skeleton_config

def config_generator(experiment_config):
    skeleton_config = experiment_config
    for k in experiment_config.K_RANGE:
        skeleton_config.K = k
        for enroll_count in experiment_config.ENROLL_COUNTS:
            skeleton_config.ENROLL_COUNT = enroll_count
            for w in experiment_config.W_RANGE:
                postfix = experiment_config.make_postfix()
                skeleton_config.MODELS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_MODELS_DIR, postfix)
                skeleton_config.DETS_DIR = make_factor_dir(experiment_config, experiment_config.BASE_DETS_DIR, postfix)
                skeleton_config.PLOT_DIR = make_factor_dir(experiment_config, experiment_config.BASE_PLOT_DIR, postfix)
                skeleton_config.MODEL_FACTORY = None # forces to setup new model factory

                skeleton_config.W = w
                wave_postfix = experiment_config.make_wave_postfix()
                
                skeleton_config.FEATURES_DIR = make_factor_dir(experiment_config, experiment_config.BASE_FEATURES_DIR,
                        wave_postfix)
                skeleton_config.setup()
            
                yield skeleton_config

def make_factor_dir(cfg, base, postfix=None):
    model_dir = os.path.join(base, postfix if postfix is not None else cfg.make_postfix())
    util.force_existence(model_dir)
    return model_dir

