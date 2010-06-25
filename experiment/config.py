import logging

import verispeak

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

    @classmethod
    def read_config(cls, dotted_name):
        import importlib
        mod = importlib.import_module(dotted_name)
        return cls(**mod.__dict__)

class ExperimentConfig(Config):
    def __init__(self, BASE_MODELS_DIR=None,
            BASE_DETS_DIR=None,
            BASE_PLOT_DIR=None,
            ENROLL_COUNTS=range(3,21),
            K_RANGE=range(2,33,2),
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

