import numpy as np

from base import Object

class TrainingProcedure(Object):
    @staticmethod
    def train(model, train_data, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.train(*args, **kwargs)

class GMMTrainingProcedure(TrainingProcedure):
    pass

class EM(GMMTrainingProcedure):
    MAX_ITERATION = 150

    GLOBAL_COV_ABS_MIN = np.float64(10.0)

    @staticmethod
    def expectation(gmm, nT, samples):
        #print "Expectation.."
        T = np.zeros((gmm.k, nT))

        for i in xrange(nT):
            sample = samples[i]
            pdfs = map(lambda c: c.pdf(sample), gmm._components)
            weighted = gmm.weights*pdfs
            T[:,i] = weighted/weighted.sum()
        #print "T:", T
        return T

    @staticmethod
    def maximization(gmm, nT, T, samples, **extra_args):
        def cov_constraint(cov):
            return
            maxi = maxj = len(cov)
            for i in range(maxi):
                for j in range(i, maxj):
                    if abs(cov[i,j]) < EM.MIN_COV:
                        print "REPLACED COV", cov[i,j]
                        cov[i,j] = cov[j,i] = EM.MIN_COV*np.sign(cov[i,j])
            #print "COV MEAN:", cov.mean(), "MIN:", cov.min()
        #print "Maximization.."
        current_likelihood = gmm.loglikelihood(samples)
        #print "current likelihood: %s;" % current_likelihood,

        gmm.weights = np.zeros(gmm.k)
        mu_vector_list = np.zeros(gmm.k).tolist()
        cov_matrix_list = np.zeros(gmm.k).tolist()
        for j in xrange(gmm.k):
            row = T[j,:]
            row_sum = row.sum()
            gmm.weights[j] = row_sum / nT

            new_mu_vector = sum(row.reshape((nT, 1))*samples) / row_sum
            mu_vector_list[j] = new_mu_vector

            def vector_sqr(v):
                return v*v.reshape((v.size, 1))
            new_cov_matrix =  sum(T[j,i]*vector_sqr(samples[i] - new_mu_vector) for i in xrange(nT)) / row_sum
            cov_constraint(new_cov_matrix)
            cov_matrix_list[j] = new_cov_matrix

        old_components = gmm._components
        gmm.reload_components(mu_vector_list, cov_matrix_list)
        new_components = gmm._components

        new_likelihood = gmm.loglikelihood(samples)
        #print "new likelihood: %s." % new_likelihood,
        print new_likelihood > current_likelihood, new_likelihood - current_likelihood

    def train(self, gmm, samples, no_init=False, max_iteration=MAX_ITERATION, **extra_args):
        if hasattr(samples, 'next'):
            samples = list(samples)
        samples = np.array(samples)

        print "Training GMM from %d samples" % (len(samples))
        if not no_init:
            gmm.initialize(samples)

        def is_enough():
            return iter_count > max_iteration

        nT = len(samples)
        iter_count = 0

        try:
            while not is_enough():
                iter_count += 1
                T = self.expectation(gmm, nT, samples)
                self.maximization(gmm, nT, T, samples, **extra_args)
        except KeyboardInterrupt:
            return iter_count

        print EM.GLOBAL_COV_ABS_MIN
        return iter_count

class DiagonalCovarianceEM(EM):
    MIN_SIGMA = 0.005

    @staticmethod
    def maximization(gmm, nT, T, samples, samples_sqr):
        def sigma_constraint(sigma_vector):
            min_sigma = DiagonalCovarianceEM.MIN_SIGMA
            #print "Sigma vector: min %s, mean %s" % (sigma_vector.min(), sigma_vector.mean())
            j=0
            for (i, sigma) in enumerate(sigma_vector):
                if sigma < min_sigma:
                    sigma_vector[i] = min_sigma
                    j += 1
            if j:
                print '%d/%d filtered' % (j, gmm.d)

        #print "Maximization.."
        current_likelihood = gmm.loglikelihood(samples)
        #print "current likelihood: %s;" % current_likelihood,

        gmm.weights = np.zeros(gmm.k)
        mu_vector_list = np.ndarray((gmm.k, gmm.d))
        sigma_vector_list = np.ndarray((gmm.k, gmm.d))
        for j in xrange(gmm.k):
            row = T[j,:]
            row_sum = row.sum()
            gmm.weights[j] = row_sum / nT

            new_mu_vector = sum(row.reshape((nT, 1))*samples) / row_sum
            mu_vector_list[j] = new_mu_vector

            new_sigma_vector = sum(row.reshape((nT, 1))*samples_sqr) / row_sum - np.square(new_mu_vector)
            sigma_constraint(new_sigma_vector)
            sigma_vector_list[j] = new_sigma_vector

        old_components = gmm._components
        gmm.reload_components(mu_vector_list, sigma_vector_list)
        new_components = gmm._components

        new_likelihood = gmm.loglikelihood(samples)
        #print "new likelihood: %s." % new_likelihood,
        print new_likelihood > current_likelihood, new_likelihood - current_likelihood

