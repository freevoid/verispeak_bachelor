import numpy as np
import math

class SingularCovarianceMatrixError(Exception):
    pass

class MultiVariateNormalDistribution(object):
    def __init__(self, mu_vector, covariance_matrix):
        super(MultiVariateNormalDistribution, self).__init__()
        self.mu = np.array(mu_vector)
        self.covariance = np.mat(covariance_matrix)
        self.n = self.mu.size
        assert(self.covariance.shape == (self.n, self.n))

        try:
            self.inv_covariance = self.covariance.getI()
        except np.linalg.LinAlgError:
            raise SingularCovarianceMatrixError

        _denominator = math.pow(math.sqrt(2*math.pi), self.n)\
                * math.sqrt(np.linalg.det(self.covariance))
        self._inv_denominator = 1.0/_denominator

    def pdf(self, x):
        x = np.array(x)
        assert (x.size == self.n)
        _x = (x - self.mu)
        return self._inv_denominator*math.exp(-0.5*_x*self.inv_covariance*_x.reshape((self.n, 1)))

