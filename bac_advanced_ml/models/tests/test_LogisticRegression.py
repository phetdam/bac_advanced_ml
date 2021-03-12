__doc__ = "Unit tests for the LogisticClassifier class."

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression as _LogisticRegression

# pylint: disable=relative-beyond-top-level
from ..supervised import LogisticRegression


def test_res(blobcls):
    """Check LogisticRegression is equivalent to sklearn for two-class case.

    Checks the fit, predict, and score methods, checking solution and accuracy.

    Parameters
    ----------
    blobcls : tuple
        pytest fixture. See conftest.py.
    """
    # unpack data from fixture
    X_train, X_test, y_train, y_test = blobcls
    # hyperparameters to fix (in case defaults change)
    shared_params = dict(tol=1e-4, C=1., max_iter=100)
    # fit scikit-learn model and our model
    _lc = _LogisticRegression(**shared_params).fit(X_train, y_train)
    lc = LogisticRegression(**shared_params).fit(X_train, y_train)
    # check that coefficients and intercepts are close. scikit-learn's coef_
    # vector has extra dimension and has intercept_ as an array.
    np.testing.assert_allclose(_lc.coef_.ravel(), lc.coef_)
    np.testing.assert_allclose(_lc.intercept_[0], lc.intercept_)
    # check that predictions are close
    np.testing.assert_allclose(_lc.predict(X_test), lc.predict(X_test))
    # accuracy should be the same
    np.testing.assert_allclose(
        _lc.score(X_test, y_test), lc.score(X_test, y_test)
    )