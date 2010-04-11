import numpy as np
import math
from itertools import imap

from stats import mvn

class Codebook(object):
    def likelihood(self, samples):
        return 0.0

    def train(self, train_samples):
        return 0

    def serialize(self):
        import cPickle
        return cPickle.dumps(self, -1)

class GMM(Codebook):
    MAX_ITERATION = 50

    def __init__(self, K=15, D=26):
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
            mvn.MultiVariateNormalDistribution(
                initial_mu.copy(), initial_cov.copy()
            ) for i in xrange(K)]

        self.reset_weights()

    def initialize(self, samples):
        initial_cov = np.eye(self.d)
        import random
        self._components = [
                mvn.MultiVariateNormalDistribution(
                    random.choice(samples),
                    np.eye(self.d))
                for j in range(self.k)]

    def reload_components(self, mu_vector_list, cov_matrix_list):
        self._components = [mvn.MultiVariateNormalDistribution(mu_vector, cov_matrix)\
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

    def train(self, samples, **kwargs):
        return self._train_em(samples, **kwargs)

    def _train_em(self, samples, no_init=False, max_iteration=MAX_ITERATION):
        if hasattr(samples, 'next'):
            samples = list(samples)

        print "Training GMM from %d samples" % (len(samples))
        if not no_init:
            self.initialize(samples)
        def expectation():
            #print "Expectation.."
            T = np.zeros((self.k, nT))

            for i in xrange(nT):
                sample = samples[i]
                pdfs = map(lambda c: c.pdf(sample), self._components)
                weighted = self.weights*pdfs
                T[:,i] = weighted/weighted.sum()
            #print "T:", T
            return T

        def maximization(T):
            #print "Maximization.."
            current_likelihood = self.loglikelihood(samples)
            #print "current likelihood: %s;" % current_likelihood,

            self.weights = np.zeros(self.k)
            mu_vector_list = np.zeros(self.k).tolist()
            cov_matrix_list = np.zeros(self.k).tolist()
            for j in xrange(self.k):
                row = T[j,:]
                row_sum = row.sum()
                self.weights[j] = row_sum / nT

                new_mu_vector = sum(row.reshape((nT, 1))*samples) / row_sum
                mu_vector_list[j] = new_mu_vector

                def vector_sqr(v):
                    return v*v.reshape((v.size, 1))
                new_cov_matrix =  sum(T[j,i]*vector_sqr(samples[i] - new_mu_vector) for i in xrange(nT)) / row_sum
                cov_matrix_list[j] = new_cov_matrix

            old_components = self._components
            self.reload_components(mu_vector_list, cov_matrix_list)
            new_components = self._components

            new_likelihood = self.loglikelihood(samples)
            #print "new likelihood: %s." % new_likelihood,
            print new_likelihood > current_likelihood, new_likelihood - current_likelihood

        def is_enough():
            return False

        nT = len(samples)
        iter_count = 0

        try:
            while not is_enough():
                iter_count += 1
                if iter_count > max_iteration:
                    break
                T = expectation()
                maximization(T)
        except KeyboardInterrupt:
            return iter_count

        return iter_count

