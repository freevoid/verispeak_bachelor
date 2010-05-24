import numpy as np

from base import Codebook
import em2.gmm

__all__ = ['Cp2DiagonalGMM']

class Cp2DiagonalGMM(Codebook):
    trainer_cls = em2.gmm.EM
    mode = 'diag'

    MAXITER = 30

    def __init__(self, K=32, D=24, mode=None):
        if mode is not None:
            self.mode = mode
        self.k = K
        self.d = D
        self.params = None
        self.gm = None
        super(Cp2DiagonalGMM, self).__init__()

    def train(self, train_samples, no_init=False, **kwargs):
        if not isinstance(train_samples, np.ndarray):
            train_samples = np.array(list(train_samples))

        if not no_init:
            w, mu, va = em2.gmm.initkmeans(train_samples, self.k)
            self.params = em2.gmm.Parameters.fromvalues(w, mu, va)
        else:
            assert(self.params is not None)

        trainer = self.trainer_cls()
        params = trainer.train(train_samples, self.params, maxiter=self.MAXITER, **kwargs)
        self.gm = em2.gm.GM.fromvalues(params.w, params.mu, params.va)
        return self.MAXITER

    def likelihood(self, samples):
        return NotImplementedError

    def loglikelihood(self, samples):
        return self.gm.pdf(samples, log=True).sum()

    def serialize(self):
        import cPickle
        gm = self.gm
        self.gm = None
        params = self.params
        self.params = None
        dump = cPickle.dumps([self, params], -1)
        self.gm = gm
        self.params = params
        return dump

    @staticmethod
    def load(filename):
        import cPickle
        [instance, params] = cPickle.load(open(filename, 'rb'))
        instance.params = params
        instance.gm = em2.gm.GM.fromvalues(params.w, params.mu, params.va)
        print type(instance.gm)
        return instance

    def get_params(self):
        return self.params.w, self.params.mu, self.params.va

