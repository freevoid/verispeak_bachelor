"""
Wrapper around GMM/EM implementation from scikits project
"""
import numpy as np
from base import GMMBase

__all__ = ['CournapeauGMM', 'CournapeauDiagonalGMM', 'AdaptedCournapeauGMM']

import cournapeau as backend

class UntrainedCournapeauGMM(GMMBase):
    model_cls = backend.GM
    mode = 'full'
 
    def __init__(self, K=32, D=24, mode=None):
        if mode is not None:
            self.mode = mode
        self.gm = self.model_cls(D, K, mode=self.mode)
        super(UntrainedCournapeauGMM, self).__init__()

    def likelihood(self, samples):
        return self.gm.pdf(samples)

    def loglikelihood(self, samples):
        #if not isinstance(samples, np.ndarray):
        #    samples = np.fromiter(samples, dtype=float)
        gmm = backend.GMM(self.gm)
        gmm.isinit = True
        return gmm.likelihood(samples)

    def serialize(self):
        import cPickle
        gm = self.gm
        self.gm = None
        dump = cPickle.dumps([self, gm], -1)
        self.gm = gm
        return dump

    @staticmethod
    def deserialize(unpickled_data):
        [instance, gm] = unpickled_data
        instance.gm = gm
        return instance

    def get_params(self):
        return self.gm.w, self.gm.mu, self.gm.va

    def set_params(self, w, mu, va):
        self.gm.set_param(w, mu, va)

from verispeak.training import MAPAdaptation
class AdaptedCournapeauGMM(UntrainedCournapeauGMM):
    training_procedure = MAPAdaptation()

class CournapeauGMM(UntrainedCournapeauGMM):
    MAXITER = 50
    trainer_cls = backend.EM
    def train(self, train_samples, no_init=False, **kwargs):
        if not isinstance(train_samples, np.ndarray):
            train_samples = np.array(list(train_samples))

        print "Training GMM from %s feature vectors" % (train_samples.shape,)

        init = 'test' if no_init else 'kmean'
        gmm = backend.GMM(self.gm, init=init)
        trainer = self.trainer_cls()
        maxiter=kwargs.pop('maxiter', self.MAXITER)
        return trainer.train(train_samples, gmm, maxiter=self.MAXITER, log=True)

class CournapeauDiagonalGMM(CournapeauGMM):
    mode = 'diag'

