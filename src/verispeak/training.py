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
    MAX_ITERATION = 30

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
        return current_likelihood, new_likelihood

    def train(self, gmm, samples,
            no_init=False, maxiter=MAX_ITERATION, thresh=1e-5,
            **extra_args):
        if hasattr(samples, 'next'):
            samples = list(samples)
        samples = np.array(samples)

        print "Training GMM from %d samples" % (len(samples))
        if not no_init:
            gmm.initialize(samples)

        def is_enough(current_likelihood, new_likelihood):
            avg = 0.5 * (current_likelihood + new_likelihood)
            delta = (new_likelihood - current_likelihood)
            return np.abs(delta / avg) < thresh

        nT = len(samples)

        try:
            for iter_count in range(maxiter):
                T = self.expectation(gmm, nT, samples)
                current_likelihood, new_likelihood = self.maximization(gmm, nT, T, samples, **extra_args)
                if is_enough(current_likelihood, new_likelihood):
                    break
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

class MAPAdaptation(GMMTrainingProcedure):
    @staticmethod
    def train(model, train_data, ubm, r=16, **kwargs):
        '''
        Overview
        --------

        Implementation of Max A Posteriori adapdation (aka Bayesian learning).
        Based on an article by Douglas Reynolds [1].
        
        Parameters
        ----------

        model : verispeak.gmm.base.GMMBase instance
            Model instance to train.
        train_data : array_like
            2D array of feature vectors.
        ubm : verispeak.gmm.base.GMMBase instance
            Model to train from.

        References
        ----------
        
        [1] Douglas A. Reynolds, Thomas F. Quatieri, Robert B. Dunn "Speaker
        Verification Using Adapted Gaussian Mixture Models", Digital Signal
        Processing 10, 19-41 (2000).
        '''
        def column_of_ones(n):
            return np.mat(np.repeat(1, n)).reshape(n, 1)

        from verispeak.gmm.cournapeau import densities
        w, mu, cov = ubm.get_params()
        k = w.size
        n, d = train_data.shape

        print "Adapting UBM to train data.."
        print ubm
        print "K=%d; D=%d; N=%d" % (k, d, n)

        pdfs = densities.multiple_gauss_den(train_data, mu, cov)
        assert pdfs.shape == (n, k)

        weighted_pdfs = w*pdfs
        assert weighted_pdfs.shape == (n, k)

        wpdf_denominators = np.array(
                weighted_pdfs # (n, k)
                    *column_of_ones(k) # (k, 1) [[1],[1],...,[1]]
                ).flatten()
        assert wpdf_denominators.shape == (n,)

        Pr = weighted_pdfs.transpose() / wpdf_denominators
        assert Pr.shape == (k, n)

        col_of_n_ones = column_of_ones(n)
        assert col_of_n_ones.shape == (n, 1)

        n_ = np.array(Pr*col_of_n_ones).flatten() # (1, k)
        assert n_.shape == (k,)

        #return locals()
        E = np.array([(np.mat(Pr[i,:])*train_data) / n_[i] for i in range(k)]).reshape((k, d))
        #E = np.array((Pr*train_data)*col_of_n_ones).flatten() / n_
        assert E.shape == (k,d)

        alpha_w = (n_ / (n_ + r))
        alpha_mu = alpha_w.reshape((k,1))
        assert alpha_mu.shape == (k,1)

        # Tuning parameters..
        adapted_w = alpha_w*n_/n + (1 - alpha_w)*w
        adapted_w /= adapted_w.sum() # normalizing
        #assert almost_eq(adapted_w.sum(), 1.0)
        
        adapted_mu = alpha_mu*E + (1 - alpha_mu)*mu

        model.set_params(adapted_w, adapted_mu, cov)
        return 1

