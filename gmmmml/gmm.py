
"""
Model data with a mixture of gaussians.
"""

import logging
import numpy as np
import scipy

from . import (em, mml)

logger = logging.getLogger(__name__)


class GaussianMixture(object):

    r"""
    Model data from many multivariate Gaussian distributions, using minimum 
    message length (MML) as the objective function.

    :param covariance_type: [optional]
        The structure of the covariance matrix for individual components.
        The available options are: `full` for a free covariance matrix, or
        `diag` for a diagonal covariance matrix (default: ``full``).

    :param covariance_regularization: [optional]
        Regularization strength to add to the diagonal of covariance matrices
        (default: ``0``).

    :param threshold: [optional]
        The relative improvement in message length required before stopping an
        expectation-maximization step (default: ``1e-5``).

    :param max_em_iterations: [optional]
        The maximum number of iterations to run per expectation-maximization
        loop (default: ``10000``).
    """

    parameter_names = ("mean", "covariance", "weight")

    def __init__(self, covariance_type="full", covariance_regularization=0, 
        threshold=1e-5, max_em_iterations=10000, **kwargs):

        available = ("full", )
        covariance_type = covariance_type.strip().lower()
        if covariance_type not in available:
            raise ValueError("covariance type '{}' is invalid. "\
                             "Must be one of: {}".format(
                                covariance_type, ", ".join(available)))

        if 0 > covariance_regularization:
            raise ValueError(
                "covariance_regularization must be a non-negative float")

        if 0 >= threshold:
            raise ValueError("threshold must be a positive value")

        if 1 > max_em_iterations:
            raise ValueError("max_em_iterations must be a positive integer")

        self._threshold = threshold
        self._max_em_iterations = max_em_iterations
        self._covariance_type = covariance_type
        self._covariance_regularization = covariance_regularization

        # Lists to record states for predictive purposes.
        self._state_K = []
        self._state_det_covs = []
        self._state_weights = []
        self._state_sum_log_weights = []
        self._state_sum_log_likelihoods = []


        #self._state_predictions_K = []
        #self._state_predictions_slog_det_covs = []
        #self._state_predictions_slog_likelihoods = []
        self._state_meta = {}

        return None


    @property
    def covariance_type(self):
        r""" Return the type of covariance stucture assumed. """
        return self._covariance_type


    @property
    def covariance_regularization(self):
        r""" 
        Return the regularization applied to diagonals of covariance matrices.
        """
        return self._covariance_regularization


    @property
    def threshold(self):
        r""" Return the threshold improvement required in message length. """
        return self._threshold


    @property
    def max_em_iterations(self):
        r""" Return the maximum number of expectation-maximization steps. """
        return self._max_em_iterations


    def search_greedy_forgetful(self, y, K_max=None, random_state=None,
        **kwargs):
        r"""
        Fit the data using a greedy search algorithm, where we do not retain
        information about previous mixtures in order to initialise the next
        set of mixtures. Instead, each new trial of :math:`K` is initialised
        using the K-means++ algorithm.

        :param y:
            The data :math:`y`.

        :param K_max: [optional]
            The maximum number of Gaussian components to consider in the
            mixture (defaults to the number of data points).

        :param random_state: [optional]
            The state to provide to the random number generator.
        """

        kwds = dict(
            threshold=self._threshold, 
            max_em_iterations=self._max_em_iterations,
            covariance_type=self.covariance_type, 
            covariance_regularization=self._covariance_regularization,
            visualization_handler=None)
        kwds.update(kwargs)
        
        y = np.atleast_1d(y)

        N, D = y.shape
        K_max = N if K_max is None else K_max
        K_predict = kwds.pop("K_predict", 25)
        visualization_handler = kwargs.get("visualization_handler", None)

        for K in range(1, K_max):

            # Initialise using k-means++.
            mu, cov, weight, responsibility = em._initialise_by_kmeans_pp(
                y, K, random_state=random_state)

            # TODO: Will giving the same random state yield the same result
            #       on every iteration?

            # Do one E-M iteration.
            R, ll, I = em.expectation(y, mu, cov, weight, **kwds)

            self._record_state(cov, weight, ll)

            mu, cov, weight = em.maximization(y, mu, cov, weight, R, **kwds)

            if visualization_handler is not None:

                # Make predictions for past and future mixtures.
                K_target = np.arange(1, weight.size + K_predict)
                self._predict_message_length(K_target, N, D, **kwds)

            raise a





        raise a



    def _record_state(self, cov, weight, log_likelihood):
        r"""
        Record the state of the model to make better predictions for the
        message lengths of future mixtures.

        :param cov:
            The covariance matrices of the current mixture.

        :param weight:
            The relative weights of the current mixture.

        :param log_likelihood:
            The log-likelihood of the current mixture.
        """

        self._state_K.append(weight.size)

        # Record determinant of covariance matrices.
        self._state_det_covs.append(np.linalg.det(cov))

        # Record weights.
        self._state_weights.append(weight)
        self._state_sum_log_weights.append(np.sum(np.log(weight)))


        # Record log-likelihood.
        self._state_sum_log_likelihoods.append(np.sum(log_likelihood))

        return None


    def _predict_message_length(self, K, N, D, **kwargs):
        """
        Predict the message length of past or future mixtures.

        :param K:
            An array-like object of the :math:`K`-th mixtures to predict the
            message elngths of.

        :param N:
            The number of data points.

        :param D:
            The dimensionality of the data points.
        """

        K = np.atleast_1d(K)

        # Predict the sum of the log of the weights.
        p_slogw, p_slogw_err, t_slogw_lower, t_slogw_upper = \
            mml.predict_sum_log_weights(K, N, 
                previous_states=(self._state_K, self._state_sum_log_weights))

        # Predict the sum of the log of the determinant of the covariance
        # matrices.
        p_slogdetcov, p_slogdetcov_err, update_state = \
            mml.predict_sum_log_det_covs(K, 
                previous_states=(self._state_K, self._state_det_covs),
                **self._state_meta)
        self._state_meta.update(update_state)





        raise a

