"""Tests for validation functions."""
# License: GNU AGPLv3

import numpy as np
import pytest
from sklearn.exceptions import DataDimensionalityWarning

from gtda.utils.validation import check_diagrams, validate_params, \
    check_point_clouds


# Testing for validate_params
def test_validate_params():
    """These tests should fail because either the type of parameters[
    parameter_name] is incorrect, or because parameter not in references[
    parameter_name]['in']."""
    references = {'par1': {'type': int, 'in': [0, 1]}}
    parameters = {'par1': 0.5}

    with pytest.raises(TypeError):
        validate_params(parameters, references)

    parameters = {'par1': 2}
    with pytest.raises(ValueError):
        validate_params(parameters, references)

    parameters = {'par0': 1}
    with pytest.raises(KeyError):
        validate_params(parameters, references)


# Testing for validate_params when one of the parameters is of list type
def test_validate_params_list():
    """Test the behaviour of validate_params on parameters which are of list
    type. Each entry in the list should satisfy the constraints described by
    references[parameter_name]['of']."""
    references = {
        'par1': {'type': list, 'of': {'type': float, 'in': [1., 2.]}}
    }
    parameters = {'par1': [1.]}

    validate_params(parameters, references)


# Testing check_diagrams
# Test for the wrong array key value
def test_inputs_keys_V():
    X = np.array([[[1, 1, 0], [2, 2, -1]]])
    with pytest.raises(ValueError):
        check_diagrams(X)


# Test for the wrong structure dimension
def test_inputs_arrayStruc_V():
    X = np.array([[[[1, 1, 0], [2, 2, 1]]]])

    with pytest.raises(ValueError):
        check_diagrams(X)


# Testing check_point_clouds
# Create several kinds of inputs
class CreateInputs:
    def __init__(
            self, n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra
    ):
        N = n_samples * n_1 * n_2
        n_1_rectang = n_1 + 1
        n_2_rectang = n_2 - 1
        N_rectang = n_samples * n_1_rectang * n_2_rectang

        self.X = np.arange(N, dtype=float).reshape(n_samples, n_1, n_2)
        self.X_rectang = np.arange(N_rectang, dtype=float). \
            reshape(n_samples, n_1_rectang, n_2_rectang)

        self.X_list = []
        self.X_list_rectang = []
        for i in range(n_samples):
            self.X_list.append(self.X[i].copy())
            self.X_list_rectang.append(self.X_rectang[i].copy())

        # List example where not all 2D arrays have the same no. of rows
        self.X_list_rectang_diff_rows = \
            self.X_list_rectang[:-1] + [self.X_list_rectang[-1][:-1, :]]

        # List example where not all 2D arrays have the same no. of columns
        self.X_list_rectang_diff_cols = \
            self.X_list_rectang[:-1] + [self.X_list_rectang[-1][:, :-1]]

        N_extra = n_samples_extra * n_1_extra * n_2_extra
        X_extra = np.arange(N_extra, dtype=float). \
            reshape(n_samples_extra, n_1_extra, n_2_extra)
        X_list_extra = []
        for i in range(n_samples_extra):
            X_list_extra.append(X_extra[i].copy())
        self.X_list_tot = self.X_list + X_list_extra

    def insert_inf(self):
        # Replace first entries with np.inf
        self.X[0, 0, 0] = np.inf
        self.X_rectang[0, 0, 0] = np.inf
        self.X_list[0][0, 0] = np.inf
        self.X_list_rectang[0][0, 0] = np.inf
        return self

    def insert_nan(self):
        # Replace first entries with np.nan
        self.X[0, 0, 0] = np.nan
        self.X_rectang[0, 0, 0] = np.nan
        self.X_list[0][0, 0] = np.nan
        self.X_list_rectang[0][0, 0] = np.nan
        return self


n_samples = 2
n_1 = 5
n_2 = 5
n_samples_extra = 1
n_1_extra = 6
n_2_extra = 6


def test_check_point_clouds_regular_finite():
    """Cases in which the input is finite and no warnings or errors should be
    thrown by check_point_clouds."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra)
    check_point_clouds(ex.X_rectang)
    check_point_clouds(ex.X_list_rectang)
    check_point_clouds(ex.X_list_rectang_diff_rows)
    check_point_clouds(ex.X, distance_matrices=True)
    check_point_clouds(ex.X_list, distance_matrices=True)
    check_point_clouds(ex.X_list_tot, distance_matrices=True)


def test_check_point_clouds_value_err_finite():
    """Cases in which the input is finite but we throw a ValueError."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra)

    # Check that we error on 1d array input
    with pytest.raises(ValueError):
        check_point_clouds(np.asarray(ex.X_list_tot))

    # Check that we error on 2d array input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X[0])

    # Check that we throw errors when arrays are not square and
    # distance_matrices is True.
    # 1) Array input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_rectang, distance_matrices=True)
    # 2) List input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_list_rectang, distance_matrices=True)


def test_check_point_clouds_warn_finite():
    """Cases in which the input is finite but we throw warnings."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra)

    # Check that we throw warnings when arrays are square and distance_matrices
    # is False
    # 1) Array input
    with pytest.warns(DataDimensionalityWarning):
        check_point_clouds(ex.X)
    # 2) List input
    with pytest.warns(DataDimensionalityWarning):
        check_point_clouds(ex.X_list)

    # Check that we throw warnings on list input when arrays have different
    # number of columns
    with pytest.warns(DataDimensionalityWarning):
        check_point_clouds(ex.X_list_rectang_diff_cols)


def test_check_point_clouds_regular_inf():
    """Cases in which part of the input is infinite and no warnings or errors
    should be thrown by check_point_clouds."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra).\
        insert_inf()

    check_point_clouds(ex.X, distance_matrices=True)
    check_point_clouds(ex.X_list, distance_matrices=True)
    check_point_clouds(ex.X_rectang, force_all_finite=False)
    check_point_clouds(ex.X_list_rectang, force_all_finite=False)


def test_check_point_clouds_value_err_inf():
    """Cases in which part of the input is infinite and we throw a
    ValueError."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra).\
        insert_inf()

    # Check that, by default, np.inf is only accepted when distance_matrices
    # is True.
    # 1) Array input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_rectang)
    # 2) List input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_list_rectang)

    # Check that we error if we explicitly set force_all_finite to True
    # 1) Array input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X, distance_matrices=True, force_all_finite=True)
    # 2) List input
    with pytest.raises(ValueError):
        check_point_clouds(
            ex.X_list, distance_matrices=True, force_all_finite=True)


def test_check_point_clouds_regular_nan():
    """Cases in which part of the input is NaN and no warnings or errors
    should be thrown by check_point_clouds."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra).\
        insert_nan()

    check_point_clouds(ex.X, distance_matrices=True,
                       force_all_finite='allow-nan')
    check_point_clouds(
        ex.X_list, distance_matrices=True, force_all_finite='allow-nan')
    check_point_clouds(ex.X_rectang, force_all_finite='allow-nan')
    check_point_clouds(ex.X_list_rectang, force_all_finite='allow-nan')


@pytest.mark.parametrize("force_all_finite", [True, False])
def test_check_point_clouds_value_err_nan(force_all_finite):
    """Cases in which part of the input is nan and we throw a
    ValueError."""

    ex = CreateInputs(
        n_samples, n_1, n_2, n_samples_extra, n_1_extra, n_2_extra).\
        insert_nan()

    # Check that we error when force_all_finite is True or False
    # 1) Array input
    with pytest.raises(ValueError):
        check_point_clouds(
            ex.X, distance_matrices=True, force_all_finite=force_all_finite)
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_rectang, force_all_finite=force_all_finite)
    # 2) List input
    with pytest.raises(ValueError):
        check_point_clouds(ex.X_list, distance_matrices=True,
                           force_all_finite=force_all_finite)
    with pytest.raises(ValueError):
        check_point_clouds(
            ex.X_list_rectang, force_all_finite=force_all_finite)
