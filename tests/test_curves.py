import math

import numpy as np
import pytest
from scipy.special import ndtr

from prv_lab.curves import gaussian_delta, gaussian_epsilon


def test_gaussian_delta_at_zero_matches_closed_form():
    noise_std = 2.0
    expected = 2.0 * ndtr(1.0 / (2.0 * noise_std)) - 1.0
    assert gaussian_delta(0.0, noise_std=noise_std) == pytest.approx(expected, abs=1e-14)


def test_curve_is_monotone_and_bounded():
    eps = np.linspace(0.0, 8.0, 101)
    delta = gaussian_delta(eps, noise_std=1.7, steps=20)
    assert np.all(delta >= 0.0)
    assert np.all(delta <= 1.0)
    assert np.all(np.diff(delta) <= 1e-14)
    assert delta[-1] < delta[0]


def test_composition_matches_effective_noise_scale():
    left = gaussian_delta(0.7, noise_std=2.0, steps=9)
    right = gaussian_delta(0.7, noise_std=2.0 / math.sqrt(9), steps=1)
    assert left == pytest.approx(right, rel=1e-12, abs=1e-14)


def test_epsilon_inversion_round_trip():
    target_epsilon = 1.25
    target_delta = gaussian_delta(target_epsilon, noise_std=1.8, steps=12)
    recovered = gaussian_epsilon(target_delta, noise_std=1.8, steps=12)
    assert recovered == pytest.approx(target_epsilon, abs=1e-9)


def test_delta_at_least_delta_zero_returns_zero_epsilon():
    delta_zero = gaussian_delta(0.0, noise_std=1.0)
    assert gaussian_epsilon(delta_zero, noise_std=1.0) == 0.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"noise_std": 0.0},
        {"noise_std": -1.0},
        {"noise_std": float("nan")},
    ],
)
def test_invalid_noise_std_rejected(kwargs):
    with pytest.raises(ValueError):
        gaussian_delta(1.0, **kwargs)


def test_negative_epsilon_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        gaussian_delta(-0.1, noise_std=1.0)


def test_invalid_delta_rejected_for_inverse():
    with pytest.raises(ValueError, match="strictly between"):
        gaussian_epsilon(0.0, noise_std=1.0)
