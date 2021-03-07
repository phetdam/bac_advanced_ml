__doc__ = """Reference implementations of supervised learning models.

Students are expected to have similar implementations.
"""

import math
import numpy as np
import scipy.sparse.linalg
import scipy.optimize
from sklearn.base import BaseEstimator
from sklearn.utils import check_array, check_X_y


class RidgeRegression(BaseEstimator):
    """Reference implementation for a ridge linear regression model.

    Parameters
    ----------
    alpha : float, default=1.0
        Regularization parameter. Increasing it increases regularization.
    solver : {"matmul", "lsqr"}
        Solver to use to compute the ridge coefficient solution. "matmul" uses
        direct inversion of the penalized moment matrix while "lsqr" uses
        scipy.sparse.linalg.lsqr to solve the damped least squares problem.

    Attributes
    ----------
    coef_ : numpy.ndarray
        Model coefficients of the fitted model, shape (n_features,)
    intercept_ : float
        Intercept (bias) term for the model.

    Methods
    -------
    fit(X, y)
        Compute coefficients to best fit the model to X, y.
    predict(X)
        Return predictions on given data X.
    score(X, y)
        Return the :math:`R^2` of the predictions.
    """
    # allowable solvers
    _solvers = ("matmul", "lsqr")

    def __init__(self, alpha = 1., solver = "lsqr"):
        if alpha < 0:
            raise ValueError("alpha must be nonnegative")
        if solver not in self._solvers:
            raise ValueError(f"solver must be one of {self._solvers}")
        self.alpha = alpha
        self.solver = solver

    def fit(self, X, y):
        """Compute coefficients to best fit the model to X, y.

        Parameters
        ----------
        X : numpy.ndarray
            Input matrix shape (n_samples, n_features)
        y : numpy.ndarray
            Response vector shape (n_samples,)

        Returns
        -------
        self
        """
        # validate input
        X, y = check_X_y(X, y)
        # compute mean of X and get centered X matrix
        x_mean = X.mean(axis = 0)
        X_c = X - x_mean
        # delegate coefficient computation to different solving methods
        if self.solver == "matmul":
            # compute coefficients using matrix inversion on centered problem
            self.coef_ = np.linalg.inv(
                X_c.T @ X_c + self.alpha * np.eye(X_c.shape[1])
            ) @ X_c.T @ y
        elif self.solver == "lsqr":
            # use scipy.sparse.linalg.lsqr to get augmented weights
            self.coef_ = scipy.sparse.linalg.lsqr(
                X_c, y, damp = math.sqrt(self.alpha)
            )[0]
        # compute intercept
        self.intercept_ = y.mean() - x_mean @ self.coef_
        # returning self allows for method chaining
        return self

    def predict(self, X):
        """Return predictions on given data X.

        Parameters
        ----------
        X : numpy.ndarray
            Input matrix shape (n_samples, n_features)

        Returns
        -------
        numpy.ndarray
            Predictions, shape (n_samples,)
        """
        if not hasattr(self, "coef_") or not hasattr(self, "intercept_"):
            raise RuntimeError("cannot predict with unfitted model")
        # validate input matrix
        X = check_array(X)
        if X.shape[1] != self.coef_.shape[0]:
            raise ValueError("n_features must match length of coef_ vector")
        return X @ self.coef_ + self.intercept_

    def score(self, X, y):
        """Return the :math:`R^2` of the predictions.

        Parameters
        ----------
        X : numpy.ndarray
            Input matrix shape (n_samples, n_features)
        y : numpy.ndarray
            Response vector shape (n_samples,)

        Returns
        -------
        float
            :math:`R^2` coefficient of determination.
        """
        # get predictions (also validates input)
        y_pred = self.predict(X)
        # return R^2
        return (
            1 - np.power(y - y_pred, 2).sum() / np.power(y - y.mean(), 2).sum()
        )


def _logistic_loss_grad(w, X, y, alpha):
    """Computes loss and gradient for a two-class logistic regression model.

    Parameters
    ----------
    w : numpy.ndarray
        Optimization variable. Contains the coefficients and the intercept, so
        it has shape (n_features + 1,).
    X : numpy.ndarray
        Input matrix, shape (n_samples, n_features)
    y : numpy.ndarray
        Response vector shape (n_samples,) where all elements are +/-1.
    alpha : float
        Regularization parameter. Equivalent to 1 / C.

    Returns
    -------
    numpy.float64
        Objective value (total loss).
    numpy.ndarray
        Gradient of the objective at w, shape (n_features + 1,).
    """
    # dummy implementation, fill it in later
    return 0


class LogisticClassifier(BaseEstimator):
    r"""Reference implementation for a logistic regression classifier.

    Only suitable for binary classification tasks. Solver used to minimize the
    objective is the scipy.optimize.minimize L-BFGS-B implementation. Objective
    is :math:`\ell^2`-regularized by default.

    Parameters
    ----------
    tol : float, default=1e-4
        Stopping tolerance to pass to solver.
    C : float, default=1.0
        Inverse regularization parameter. Increase to reduce regularization.
    max_iter : int, default=100
        Maximum number of iterations that L-BFGS-B is allowed to execute.

    Attributes
    ----------
    classes_ : numpy.ndarray
        Array of class labels known to the classifier, shape (n_classes,)
    coef_ : numpy.ndarray
        Model coefficients of the fitted model, shape (n_features,)
    intercept_ : float
        Intercept (bias) term for the model.

    Methods
    -------
    fit(X, y)
        Compute coefficients to best fit the model to X, y.
    predict(X)
        Return predictions on given data X.
    score(X, y)
        Return the accuracy of the predictions.
    """
    def __init__(self, tol = 1e-4, C = 1., max_iter = 100):
        if tol <= 0:
            raise ValueError("tol must be positive")
        if C <= 0:
            raise ValueError("C must be positive")
        if max_iter <= 0:
            raise ValueError("max_iter must be positive")
        self.tol = tol
        self.C = C
        self.max_iter = max_iter

    def fit(self, X, y):
        # validate input
        X, y = check_X_y(X, y)
        # get n_samples, n_features
        n_samples, n_features = X.shape
        # get number of unique labels in y. if labels.size != 2, raise error
        labels = np.unique(y)
        if labels.size != 2:
            raise ValueError(
                "Cannot fit coefficients on non-binary classification tasks"
            )
        # get mask of +1, -1
        y_mask = np.empty(y.shape)
        y_mask[y == labels[0]] = 1
        y_mask[y == labels[1]] = -1
        # solve for coefficients and intercept
        weights = scipy.optimize.minimize(
            _logistic_loss_grad, np.zeros(n_features + 1), method = "L-BFGS-B",
            jac = True, args = (X, y_mask, 1. / C),
            options = {"gtol": self.tol, "maxiter": self.max_iter}
        )
        self.coef_ = weights[:-1]
        self.intercept_ = weights[-1]
        # return self to allow for method chaining
        return self

    def predict(self, X):
        raise NotImplementedError("predict method not implemented yet")

    def score(self, X, y):
        raise NotImplementedError("score method not implemented yet")