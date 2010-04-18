import numpy as np
import math

class SingularCovarianceMatrixError(Exception):
    pass

class MultiVariateNormalDistribution(object):
    sqrt_2_pi = math.sqrt(2*math.pi)
    det_min = 1.0
    def __init__(self, mu_vector, covariance_matrix, **kwargs):
        super(MultiVariateNormalDistribution, self).__init__()
        self.mu = np.array(mu_vector)
        self.covariance = np.mat(covariance_matrix)
        self.n = self.mu.size
        assert(self.covariance.shape == (self.n, self.n))

        try:
            self.inv_covariance = self.covariance.getI()
        except np.linalg.LinAlgError:
            raise SingularCovarianceMatrixError

        det = np.linalg.det(self.covariance)
        #print "DET:", det
        if det < 0:
            print "ALARM! DET IS NEGATIVE!", det
            det = self.__class__.det_min
        else:
            self.__class__.det_min = min(det, self.__class__.det_min)
            
        #print "SQRTDET:", math.sqrt(det)
        _denominator = math.pow(self.sqrt_2_pi, self.n)\
                * math.sqrt(det)
        self._inv_denominator = 1.0/_denominator
        #print "INV_DENOMINATOR:", self._inv_denominator

    def pdf(self, x):
        x = np.array(x)
        assert (x.size == self.n)
        _x = (x - self.mu)
        exp = -0.5*_x*self.inv_covariance*_x.reshape((self.n, 1))
        try:
            return self._inv_denominator*math.exp(exp)
        except OverflowError:
            print "Overflow during pdf:("
            logpdf = math.log(self._inv_denominator) + exp
            "LOGPDF:",  math.log(self._inv_denominator) + exp
            return math.exp(logpdf)

    def logpdf(self, x):
        x = np.array(x)
        assert (x.size == self.n)
        _x = (x - self.mu)
        exp = -0.5*_x*self.inv_covariance*_x.reshape((self.n, 1))
        return math.log(self._inv_denominator) + exp

class DiagonalCovarianceMVN(MultiVariateNormalDistribution):
    def __init__(self, mu_vector, sigma_vector):
        object.__init__(self)
        self.mu = np.array(mu_vector)
        if len(sigma_vector.shape) == 2 and sigma_vector.shape[0] == sigma_vector.shape[1]: # if got covariance matrix instead of sigma vector
            sigma_vector = sigma_vector.diagonal()
        self.covariance = np.array(sigma_vector)
        self.n = self.mu.size
        assert(self.covariance.shape == self.mu.shape)

        try:
            self.inv_covariance = 1 / self.covariance
        except np.linalg.LinAlgError:
            raise SingularCovarianceMatrixError

        _denominator = math.pow(self.sqrt_2_pi, self.n)\
                * math.sqrt(self.covariance.prod())
        self._inv_denominator = 1.0/_denominator

    def pdf(self, x):
        x = np.array(x)
        assert(x.size == self.n)

        exp = (self.inv_covariance*np.square(x - self.mu)).sum()
        return self._inv_denominator*np.exp(-0.5*exp)

    def logpdf(self, x):
        x = np.array(x)
        assert(x.size == self.n)

        exp = (self.inv_covariance*np.square(x - self.mu)).sum()
        return math.log(self._inv_denominator) - 0.5*exp

