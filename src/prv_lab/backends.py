"""Adapters for established privacy-accounting implementations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


class OptionalDependencyError(ImportError):
    """Raised when a requested optional accounting backend is not installed."""


@dataclass(frozen=True)
class CurvePoint:
    epsilon: float
    delta_lower: float
    delta_estimate: float
    delta_upper: float


@dataclass(frozen=True)
class EpsilonResult:
    delta: float
    epsilon_lower: float
    epsilon_estimate: float
    epsilon_upper: float


def _load_prv_symbols() -> tuple[Any, Any, Any]:
    try:
        from prv_accountant import (  # type: ignore[import-not-found]
            GaussianMechanism,
            PoissonSubsampledGaussianMechanism,
            PRVAccountant,
        )
    except ImportError as exc:
        raise OptionalDependencyError(
            "The official PRV backend is optional. Install it with: pip install 'prv-lab[prv]'"
        ) from exc
    return PRVAccountant, GaussianMechanism, PoissonSubsampledGaussianMechanism


def dpsgd_delta_curve(
    epsilons: list[float],
    *,
    sampling_probability: float,
    noise_multiplier: float,
    steps: int,
    eps_error: float = 0.01,
    delta_error: float = 1e-12,
) -> list[CurvePoint]:
    """Compute a DP-SGD privacy curve using Microsoft's PRV Accountant.

    The accountant is configured once and reused for all epsilon values. Returned
    lower/estimate/upper values are the values exposed by that library; they are
    not silently replaced by the estimate alone.
    """
    _validate_dpsgd_inputs(
        sampling_probability, noise_multiplier, steps, eps_error, delta_error
    )
    if not epsilons:
        raise ValueError("epsilons must contain at least one value")
    if any(not math.isfinite(float(e)) or float(e) < 0 for e in epsilons):
        raise ValueError("epsilon values must be finite and non-negative")

    PRVAccountant, _, SubsampledGaussian = _load_prv_symbols()
    mechanism = SubsampledGaussian(
        noise_multiplier=float(noise_multiplier),
        sampling_probability=float(sampling_probability),
    )
    accountant = PRVAccountant(
        prvs=[mechanism],
        max_self_compositions=[int(steps)],
        eps_error=float(eps_error),
        delta_error=float(delta_error),
    )

    points: list[CurvePoint] = []
    for epsilon in epsilons:
        lower, estimate, upper = accountant.compute_delta(
            epsilon=float(epsilon), num_self_compositions=[int(steps)]
        )
        points.append(
            CurvePoint(
                epsilon=float(epsilon),
                delta_lower=float(lower),
                delta_estimate=float(estimate),
                delta_upper=float(upper),
            )
        )
    return points


def dpsgd_epsilon(
    *,
    delta: float,
    sampling_probability: float,
    noise_multiplier: float,
    steps: int,
    eps_error: float = 0.01,
    delta_error: float | None = None,
) -> EpsilonResult:
    """Compute epsilon bounds for Poisson-subsampled Gaussian DP-SGD."""
    if not 0.0 < float(delta) < 1.0:
        raise ValueError("delta must be strictly between zero and one")
    if delta_error is None:
        delta_error = float(delta) / 1000.0
    _validate_dpsgd_inputs(
        sampling_probability, noise_multiplier, steps, eps_error, delta_error
    )

    PRVAccountant, _, SubsampledGaussian = _load_prv_symbols()
    mechanism = SubsampledGaussian(
        noise_multiplier=float(noise_multiplier),
        sampling_probability=float(sampling_probability),
    )
    accountant = PRVAccountant(
        prvs=[mechanism],
        max_self_compositions=[int(steps)],
        eps_error=float(eps_error),
        delta_error=float(delta_error),
    )
    lower, estimate, upper = accountant.compute_epsilon(
        delta=float(delta), num_self_compositions=[int(steps)]
    )
    return EpsilonResult(
        delta=float(delta),
        epsilon_lower=float(lower),
        epsilon_estimate=float(estimate),
        epsilon_upper=float(upper),
    )


def validate_gaussian_with_prv(
    epsilons: list[float],
    *,
    noise_std: float,
    steps: int,
    eps_error: float = 0.01,
    delta_error: float = 1e-12,
) -> list[CurvePoint]:
    """Compute PRV Accountant estimates for an unsampled Gaussian mechanism."""
    if not _finite_positive(noise_std):
        raise ValueError("noise_std must be finite and greater than zero")
    if isinstance(steps, bool) or int(steps) != steps or int(steps) < 1:
        raise ValueError("steps must be a positive integer")
    if not epsilons or any(not math.isfinite(float(e)) or float(e) < 0 for e in epsilons):
        raise ValueError("epsilons must be a non-empty list of finite non-negative values")
    if not _finite_positive(eps_error):
        raise ValueError("eps_error must be finite and greater than zero")
    if not 0.0 < float(delta_error) < 1.0:
        raise ValueError("delta_error must be strictly between zero and one")

    PRVAccountant, GaussianMechanism, _ = _load_prv_symbols()
    mechanism = GaussianMechanism(noise_multiplier=float(noise_std))
    accountant = PRVAccountant(
        prvs=[mechanism],
        max_self_compositions=[int(steps)],
        eps_error=float(eps_error),
        delta_error=float(delta_error),
    )
    points: list[CurvePoint] = []
    for epsilon in epsilons:
        lower, estimate, upper = accountant.compute_delta(
            epsilon=float(epsilon), num_self_compositions=[int(steps)]
        )
        points.append(
            CurvePoint(
                epsilon=float(epsilon),
                delta_lower=float(lower),
                delta_estimate=float(estimate),
                delta_upper=float(upper),
            )
        )
    return points


def _validate_dpsgd_inputs(
    sampling_probability: float,
    noise_multiplier: float,
    steps: int,
    eps_error: float,
    delta_error: float,
) -> None:
    if not 0.0 < float(sampling_probability) <= 1.0:
        raise ValueError("sampling_probability must be in (0, 1]")
    if not _finite_positive(noise_multiplier):
        raise ValueError("noise_multiplier must be finite and greater than zero")
    if isinstance(steps, bool) or int(steps) != steps or int(steps) < 1:
        raise ValueError("steps must be a positive integer")
    if not _finite_positive(eps_error):
        raise ValueError("eps_error must be finite and greater than zero")
    if not 0.0 < float(delta_error) < 1.0:
        raise ValueError("delta_error must be strictly between zero and one")


def _finite_positive(value: float) -> bool:
    return math.isfinite(float(value)) and float(value) > 0.0
