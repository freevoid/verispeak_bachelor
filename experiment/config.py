import logging

import verispeak

class Config(object):
    def __init__(self,
            WAV_DIR='./data/wav',
            MODELS_DIR='./data/models',
            FEATURES_DIR='./data/features',
            DETS_DIR='./data/dets',
            PLOT_DIR='./data/plots',
            MODEL_FACTORY = lambda: verispeak.gmm.CournapeauGMM(K=16),
            ENROLL_COUNT=10,
            UBM_PATH='./data/ubm/ubm16.gmm',
            PLOT_FORMAT='pdf',
            LOGGING_LEVEL=logging.DEBUG,
            **unhandled):
        del unhandled # forget about not supported options
        self.__dict__ = locals()
        self.setup()

    def setup(self):
        logging.basicConfig(level=self.LOGGING_LEVEL)

    @classmethod
    def read_config(cls, dotted_name):
        mod = __import__(dotted_name)
        return cls(**mod.__dict__)


