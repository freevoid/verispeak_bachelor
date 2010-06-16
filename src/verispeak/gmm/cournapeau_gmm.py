"""
Wrapper around GMM/EM implementation from scikits project
"""
import numpy as np
from base import Codebook

__all__ = ['CournapeauGMM', 'CournapeauDiagonalGMM']

import cournapeau as em
class CournapeauGMM(Codebook):
    MAXITER = 30
    trainer_cls = em.EM
    model_cls = em.GM
    mode = 'full'
    def __init__(self, K=32, D=24, mode=None):
        if mode is not None:
            self.mode = mode
        self.gm = self.model_cls(D, K, mode=self.mode)
        super(CournapeauGMM, self).__init__()

    def train(self, train_samples, no_init=False, **kwargs):
        if not isinstance(train_samples, np.ndarray):
            train_samples = np.array(list(train_samples))

        print "Training GMM from %s feature vectors" % (train_samples.shape,)

        init = 'test' if no_init else 'kmean'
        gmm = em.GMM(self.gm, init=init)
        trainer = self.trainer_cls()
        return trainer.train(train_samples, gmm, maxiter=self.MAXITER, log=True, **kwargs)

    def likelihood(self, samples):
        return self.gm.pdf(samples)

    def loglikelihood(self, samples):
        #if not isinstance(samples, np.ndarray):
        #    samples = np.fromiter(samples, dtype=float)
        gmm = em.GMM(self.gm)
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

class CournapeauDiagonalGMM(CournapeauGMM):
    mode = 'diag'

