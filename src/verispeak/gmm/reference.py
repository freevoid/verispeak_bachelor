"""
Reference implementation of Gaussian Mixture Model with K-means initialization.
Using reference EM training algorithm.
"""
import numpy as np
import math
from itertools import imap

from base import Codebook
from verispeak.training import EM, DiagonalCovarianceEM
from verispeak.stats import mvn

__all__ = ['GMM', 'DiagonalGMM']
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

