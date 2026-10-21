"""Analytic privacy curves used as reference checks.

The Gaussian formula in this module is exact for a non-subsampled Gaussian
mechanism with sensitivity ``sensitivity`` and additive Gaussian noise with
standard deviation ``noise_std``. Repeating the same mechanism independently
``steps`` times is equivalent, for this curve, to a Gaussian mechanism with
squared Mahalanobis shift ``steps * (sensitivity / noise_std) ** 2``.

This is not a formula for Poisson-subsampled DP-SGD; use the optional PRV
backend for that mechanism.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import brentq
from scipy.special import log_ndtr, ndtr

FloatArray = NDArray[np.float64]


def _validate_positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite number greater than zero")
    return value


def gaussian_delta(
    epsilon: float | Iterable[float] | NDArray[np.float64],
    *,
    noise_std: float,
    sensitivity: float = 1.0,
    steps: int = 1,
) -> float | FloatArray:
    r"""Return the exact :math:`\delta(\epsilon)` curve for Gaussian composition.

    Parameters
    ----------
    epsilon:
        Non-negative epsilon value or one-dimensional collection of values.
    noise_std:
        Standard deviation of the noise added by each mechanism.
    sensitivity:
        L2 sensitivity of each query. Defaults to 1.
    steps:
        Number of independently composed, identically parameterized mechanisms.

    Notes
    -----
    With ``mu = sqrt(steps) * sensitivity / noise_std``, the curve is

    ``Phi(mu/2 - epsilon/mu) - exp(epsilon) * Phi(-mu/2 - epsilon/mu)``.

    ``log_ndtr`` is used for the second term to reduce underflow/overflow risk.
    The result is clipped to [0, 1] to remove tiny floating-point excursions.
    """
    noise_std = _validate_positive_finite("noise_std", noise_std)
    sensitivity = _validate_positive_finite("sensitivity", sensitivity)
    if isinstance(steps, bool) or not isinstance(steps, (int, np.integer)) or steps < 1:
        raise ValueError("steps must be a positive integer")

    eps = np.asarray(epsilon, dtype=np.float64)
    if not np.all(np.isfinite(eps)) or np.any(eps < 0):
        raise ValueError("epsilon values must be finite and non-negative")

    mu = math.sqrt(int(steps)) * sensitivity / noise_std
    first = ndtr(mu / 2.0 - eps / mu)
    log_second = eps + log_ndtr(-mu / 2.0 - eps / mu)
    with np.errstate(under="ignore", over="ignore", invalid="ignore"):
        second = np.exp(log_second)
    delta = np.clip(first - second, 0.0, 1.0)

    if eps.ndim == 0:
        return float(delta)
    return np.asarray(delta, dtype=np.float64)


def gaussian_epsilon(
    delta: float,
    *,
    noise_std: float,
    sensitivity: float = 1.0,
    steps: int = 1,
    max_epsilon: float = 1_000_000.0,
) -> float:
    """Invert the exact Gaussian curve for a target ``delta``.

    Returns the smallest non-negative epsilon whose curve value is at most
    ``delta``. For ``delta >= delta(0)``, the result is zero. Delta must be
    strictly positive; a zero target generally corresponds to infinite epsilon.
    """
    delta = float(delta)
    if not math.isfinite(delta) or not 0.0 < delta < 1.0:
        raise ValueError("delta must be finite and strictly between zero and one")
    max_epsilon = _validate_positive_finite("max_epsilon", max_epsilon)
    at_zero = float(
        gaussian_delta(0.0, noise_std=noise_std, sensitivity=sensitivity, steps=steps)
    )
    if delta >= at_zero:
        return 0.0

    lo, hi = 0.0, 1.0
    while hi < max_epsilon and float(
        gaussian_delta(hi, noise_std=noise_std, sensitivity=sensitivity, steps=steps)
    ) > delta:
        hi = min(hi * 2.0, max_epsilon)

    if float(gaussian_delta(hi, noise_std=noise_std, sensitivity=sensitivity, steps=steps)) > delta:
        raise RuntimeError(
            "Could not bracket epsilon before max_epsilon; increase max_epsilon or inspect inputs"
        )
    return float(
        brentq(
            lambda eps: float(
                gaussian_delta(eps, noise_std=noise_std, sensitivity=sensitivity, steps=steps)
            )
            - delta,
            lo,
            hi,
            xtol=1e-12,
            rtol=1e-12,
        )
    )
