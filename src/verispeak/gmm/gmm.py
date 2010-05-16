import numpy as np
import math
from itertools import imap
from functools import partial as curry

from verispeak.stats import mvn
from verispeak.base import Object
from verispeak.training import EM, DiagonalCovarianceEM

__all__ = ['Codebook', 'CournapeauGMM', 'CournapeauDiagonalGMM',
    'GMM', 'DiagonalGMM', 'Cp2DiagonalGMM']

class Codebook(Object):
    training_procedure = None

    def __init__(self):
        self.iterations = 0

    def likelihood(self, samples):
        return 0.0

    def train(self, train_samples, **kwargs):
        """
        Train the codebook on a train samples.

        @retval: number of iterations
        @val train_samples: iterable of numpy arrays (feature vectors)
        """
        iterations = self.training_procedure(self, train_samples, **kwargs)
        if kwargs.get('no_init'):
            self.iterations += iterations
        else:
            self.iterations = iterations
        return iterations

    def serialize(self):
        import cPickle
        return cPickle.dumps(self, -1)
        training_procedure = self.training_procedure
        self.training_procedure = None
        dump = cPickle.dumps(self, -1)
        self.training_procedure = training_procedure
        return dump

    def dump_to_file(self, filename):
        f = open(filename, "wb")
        f.write(self.serialize())
        f.close()
        return True

    @staticmethod
    def load(filename):
        import cPickle
        f = open(filename)
        return cPickle.load(f)

import cournapeau as em
class CournapeauGMM(Codebook):
    MAXITER = 30
    trainer_cls = em.gmm_em.EM
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

        init = 'test' if no_init else 'kmean'
        gmm = em.GMM(self.gm, init=init)
        trainer = self.trainer_cls()
        return trainer.train(train_samples, gmm, maxiter=self.MAXITER, log=True, **kwargs)

    def likelihood(self, samples):
        return self.gm.pdf(samples)

    def loglikelihood(self, samples):
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
    def load(filename):
        import cPickle
        [instance, gm] = cPickle.load(open(filename, 'rb'))
        instance.gm = gm
        return instance

    def get_params(self):
        return self.gm.w, self.gm.mu, self.gm.va

class CournapeauDiagonalGMM(CournapeauGMM):
    mode = 'diag'

import em2.gmm
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

class GMM(Codebook):
    training_procedure = EM()
    mvn_dist = mvn.MultiVariateNormalDistribution
    mode = 'full'

    def __init__(self, K=16, D=24):
        """
        @var D: number of dimensions
        @var K: quantity of Gaussian components
        """
        super(GMM, self).__init__()
        self._k = K
        self._d = D

        initial_mu = np.zeros(D)
        initial_cov = np.eye(D)
        self._components = [
            self.mvn_dist(
                initial_mu.copy(), initial_cov.copy()
            ) for i in xrange(K)]

        self.reset_weights()

    def initialize(self, samples):
        initial_cov = np.eye(self.d)
        import random
        initial_cov = np.eye(self.d)
        self._components = [
                self.mvn_dist(
                    random.choice(samples),
                    initial_cov.copy())
                for j in range(self.k)]

    def initialize(self, data, niter=5):
        from scipy.cluster.vq import kmeans2 as kmeans

        d = self.d
        k = self.k
        (code, label) = kmeans(data, self.k, niter, minit='random')

        nsamples = float(len(data))
        w   = np.ones(k)# / k
        for i in range(k):
            w[i] = len(np.where(label==i)[0]) / nsamples

        mu  = code.copy()
        if self.mode == 'diag':
            va = np.zeros((k, d))
            for i in range(k):
                for j in range(d):
                    va[i, j] = np.cov(data[np.where(label==i), j], rowvar = 0)
        elif self.mode == 'full':
            va  = np.zeros((k*d, d))
            for i in range(k):
                va[i*d:i*d+d, :] = \
                    np.cov(data[np.where(label==i)], rowvar = 0)
            va = va.reshape((k, d, d))
        else:
            raise AttributeError("mode " + str(self.mode) + \
                    " not recognized")

        self.weights = w
        self.reload_components(mu, va)
        print "K-MEANS initialization done!"

    def reload_components(self, mu_vector_list, cov_matrix_list):
        self._components = [self.mvn_dist(mu_vector, cov_matrix)\
                for (mu_vector, cov_matrix)\
                    in zip(mu_vector_list, cov_matrix_list)]

    def get_component(self, i):
        return self._components[i]

    @property
    def k(self): return self._k
    @property
    def d(self): return self._d

    def likelihood(self, x_samples):
        return reduce(lambda acc, x: acc*self.p(x), x_samples, 1.0)

    def loglikelihood(self, x_samples):
        p_array = np.array(map(self.p, x_samples))
        return np.log(p_array).sum()
        return sum(imap(math.log, imap(self.p, x_samples)))

    def p(self, x):
        return sum(
                self.weights*map(
                    lambda comp: comp.pdf(x), self._components))

    def reset_weights(self):
        self.weights = np.repeat(1.0/self.k, self.k)

    def get_params(self):
        mu = np.array([c.mu for c in self._components])
        va = np.array([c.covariance.diagonal() for c in self._components]).reshape((self.k, self.d))
        return self.weights, mu, va

    def __unicode__(self):
        return u"k=%d d=%d iterations=%d" % (self.k, self.d, self.iterations)

class DiagonalGMM(GMM):
    training_procedure = DiagonalCovarianceEM()
    mvn_dist = mvn.DiagonalCovarianceMVN
    mode = 'diag'

    def train(self, samples, **kwargs):
        samples = np.array(list(samples))
        kwargs.update({'samples_sqr': np.square(samples)})
        return super(DiagonalGMM, self).train(samples, **kwargs)

    def get_params(self):
        mu = np.array([c.mu for c in self._components])
        va = np.array([c.covariance for c in self._components])
        return self.weights, mu, va

