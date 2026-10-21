"""Command-line interface for PRV-Lab."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np

from prv_lab import __version__
from prv_lab.backends import (
    OptionalDependencyError,
    dpsgd_delta_curve,
    dpsgd_epsilon,
    validate_gaussian_with_prv,
)
from prv_lab.curves import gaussian_delta
from prv_lab.io_utils import run_metadata, write_csv, write_json


def _positive_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if result < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return result


def _positive_float(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return result


def _nonnegative_float(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("must be finite and non-negative")
    return result


def _common_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/run"),
        help="Output directory",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prv-lab",
        description="Reproducible privacy-accounting experiments and PRV curve diagnostics.",
    )
    parser.add_argument("--version", action="version", version=f"prv-lab {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gaussian = subparsers.add_parser(
        "gaussian-curve",
        help="Compute the exact curve for repeated non-subsampled Gaussian mechanisms.",
    )
    gaussian.add_argument("--noise-std", type=_positive_float, required=True)
    gaussian.add_argument("--sensitivity", type=_positive_float, default=1.0)
    gaussian.add_argument("--steps", type=_positive_int, default=1)
    gaussian.add_argument("--eps-min", type=_nonnegative_float, default=0.0)
    gaussian.add_argument("--eps-max", type=_positive_float, default=5.0)
    gaussian.add_argument("--points", type=_positive_int, default=201)
    _common_output(gaussian)

    curve = subparsers.add_parser(
        "dpsgd-curve",
        help="Compute a Poisson-subsampled Gaussian DP-SGD curve with PRV Accountant.",
    )
    curve.add_argument("--sampling-probability", type=_positive_float, required=True)
    curve.add_argument("--noise-multiplier", type=_positive_float, required=True)
    curve.add_argument("--steps", type=_positive_int, required=True)
    curve.add_argument("--eps-min", type=_nonnegative_float, default=0.0)
    curve.add_argument("--eps-max", type=_positive_float, default=5.0)
    curve.add_argument("--points", type=_positive_int, default=201)
    curve.add_argument("--eps-error", type=_positive_float, default=0.01)
    curve.add_argument("--delta-error", type=_positive_float, default=1e-12)
    _common_output(curve)

    epsilon = subparsers.add_parser(
        "dpsgd-epsilon", help="Compute epsilon bounds for a DP-SGD run with PRV Accountant."
    )
    epsilon.add_argument("--sampling-probability", type=_positive_float, required=True)
    epsilon.add_argument("--noise-multiplier", type=_positive_float, required=True)
    epsilon.add_argument("--steps", type=_positive_int, required=True)
    epsilon.add_argument("--delta", type=_positive_float, required=True)
    epsilon.add_argument("--eps-error", type=_positive_float, default=0.01)
    epsilon.add_argument("--delta-error", type=_positive_float, default=None)
    _common_output(epsilon)

    validate = subparsers.add_parser(
        "validate-gaussian",
        help="Compare PRV Accountant curve estimates with the analytic Gaussian reference.",
    )
    validate.add_argument("--noise-std", type=_positive_float, required=True)
    validate.add_argument("--steps", type=_positive_int, default=1)
    validate.add_argument("--eps-min", type=_nonnegative_float, default=0.0)
    validate.add_argument("--eps-max", type=_positive_float, default=5.0)
    validate.add_argument("--points", type=_positive_int, default=101)
    validate.add_argument("--eps-error", type=_positive_float, default=0.01)
    validate.add_argument("--delta-error", type=_positive_float, default=1e-12)
    _common_output(validate)
    return parser


def _check_grid(eps_min: float, eps_max: float, points: int) -> np.ndarray:
    if eps_max <= eps_min:
        raise ValueError("eps-max must be greater than eps-min")
    if points < 2:
        raise ValueError("points must be at least 2")
    return np.linspace(eps_min, eps_max, points, dtype=np.float64)


def _plot_curve(
    path: Path,
    epsilons: np.ndarray,
    curves: list[tuple[str, np.ndarray]],
    *,
    title: str,
    ylabel: str = "delta",
    log_y: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    for label, values in curves:
        values = np.asarray(values, dtype=float)
        if log_y:
            values = np.maximum(values, np.finfo(float).tiny)
        ax.plot(epsilons, values, label=label, linewidth=2)
    if log_y:
        ax.set_yscale("log")
    ax.set_xlabel("epsilon")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _run_gaussian(args: argparse.Namespace) -> int:
    eps = _check_grid(args.eps_min, args.eps_max, args.points)
    delta = gaussian_delta(
        eps, noise_std=args.noise_std, sensitivity=args.sensitivity, steps=args.steps
    )
    rows = [
        {"epsilon": float(e), "delta": float(d)} for e, d in zip(eps, delta, strict=True)
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "gaussian_curve.csv", rows)
    _plot_curve(
        args.output_dir / "gaussian_curve.png",
        eps,
        [("Exact Gaussian composition", delta)],
        title="Exact Gaussian privacy curve",
    )
    params = {
        "noise_std": args.noise_std,
        "sensitivity": args.sensitivity,
        "steps": args.steps,
        "eps_min": args.eps_min,
        "eps_max": args.eps_max,
        "points": args.points,
        "assumption": "non-subsampled Gaussian mechanism; identical independent steps",
    }
    write_json(args.output_dir / "run_metadata.json", run_metadata(args.command, params))
    print(f"Wrote {len(rows)} curve points to {args.output_dir.resolve()}")
    print(f"delta(epsilon=0) = {float(delta[0]):.8g}")
    print(f"delta(epsilon={eps[-1]:g}) = {float(delta[-1]):.8g}")
    return 0


def _run_dpsgd_curve(args: argparse.Namespace) -> int:
    eps = _check_grid(args.eps_min, args.eps_max, args.points)
    points = dpsgd_delta_curve(
        [float(x) for x in eps],
        sampling_probability=args.sampling_probability,
        noise_multiplier=args.noise_multiplier,
        steps=args.steps,
        eps_error=args.eps_error,
        delta_error=args.delta_error,
    )
    rows = [
        {
            "epsilon": p.epsilon,
            "delta_lower": p.delta_lower,
            "delta_estimate": p.delta_estimate,
            "delta_upper": p.delta_upper,
        }
        for p in points
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "dpsgd_curve.csv", rows)
    _plot_curve(
        args.output_dir / "dpsgd_curve.png",
        eps,
        [
            ("PRV estimate", np.array([p.delta_estimate for p in points])),
            ("PRV lower bound", np.maximum([p.delta_lower for p in points], 0.0)),
            ("PRV upper bound", np.maximum([p.delta_upper for p in points], 0.0)),
        ],
        title="DP-SGD privacy curve (PRV Accountant)",
    )
    params = {
        "sampling_probability": args.sampling_probability,
        "noise_multiplier": args.noise_multiplier,
        "steps": args.steps,
        "eps_min": args.eps_min,
        "eps_max": args.eps_max,
        "points": args.points,
        "eps_error": args.eps_error,
        "delta_error": args.delta_error,
        "backend": "microsoft/prv_accountant",
    }
    write_json(args.output_dir / "run_metadata.json", run_metadata(args.command, params))
    print(f"Wrote {len(rows)} curve points to {args.output_dir.resolve()}")
    return 0


def _run_dpsgd_epsilon(args: argparse.Namespace) -> int:
    result = dpsgd_epsilon(
        delta=args.delta,
        sampling_probability=args.sampling_probability,
        noise_multiplier=args.noise_multiplier,
        steps=args.steps,
        eps_error=args.eps_error,
        delta_error=args.delta_error,
    )
    row = {
        "delta": result.delta,
        "epsilon_lower": result.epsilon_lower,
        "epsilon_estimate": result.epsilon_estimate,
        "epsilon_upper": result.epsilon_upper,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "dpsgd_epsilon.csv", [row])
    params = {
        "sampling_probability": args.sampling_probability,
        "noise_multiplier": args.noise_multiplier,
        "steps": args.steps,
        "delta": args.delta,
        "eps_error": args.eps_error,
        "delta_error": args.delta_error,
        "backend": "microsoft/prv_accountant",
    }
    write_json(args.output_dir / "run_metadata.json", run_metadata(args.command, params))
    print(f"epsilon lower / estimate / upper: {result.epsilon_lower:.8g} / "
          f"{result.epsilon_estimate:.8g} / {result.epsilon_upper:.8g}")
    print(f"Wrote results to {args.output_dir.resolve()}")
    return 0


def _run_validate_gaussian(args: argparse.Namespace) -> int:
    eps = _check_grid(args.eps_min, args.eps_max, args.points)
    points = validate_gaussian_with_prv(
        [float(x) for x in eps],
        noise_std=args.noise_std,
        steps=args.steps,
        eps_error=args.eps_error,
        delta_error=args.delta_error,
    )
    exact = np.asarray(
        gaussian_delta(eps, noise_std=args.noise_std, sensitivity=1.0, steps=args.steps),
        dtype=float,
    )
    rows: list[dict[str, Any]] = []
    covered = 0
    for e, exact_delta, point in zip(eps, exact, points, strict=True):
        is_covered = point.delta_lower <= exact_delta <= point.delta_upper
        covered += int(is_covered)
        rows.append(
            {
                "epsilon": float(e),
                "delta_exact": float(exact_delta),
                "delta_lower": point.delta_lower,
                "delta_estimate": point.delta_estimate,
                "delta_upper": point.delta_upper,
                "exact_inside_reported_interval": is_covered,
                "absolute_estimate_error": abs(point.delta_estimate - float(exact_delta)),
            }
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "gaussian_validation.csv", rows)
    _plot_curve(
        args.output_dir / "gaussian_validation.png",
        eps,
        [
            ("Analytic reference", exact),
            ("PRV estimate", np.array([p.delta_estimate for p in points])),
        ],
        title="PRV Accountant vs exact Gaussian reference",
    )
    params = {
        "noise_std": args.noise_std,
        "steps": args.steps,
        "eps_min": args.eps_min,
        "eps_max": args.eps_max,
        "points": args.points,
        "eps_error": args.eps_error,
        "delta_error": args.delta_error,
        "backend": "microsoft/prv_accountant",
    }
    metadata = run_metadata(args.command, params)
    metadata["coverage_diagnostic"] = {
        "points_inside_reported_interval": covered,
        "points_total": len(points),
        "fraction_inside_reported_interval": covered / len(points),
        "warning": (
            "Diagnostic only; investigate failures before interpreting backend guarantees."
        ),
    }
    write_json(args.output_dir / "run_metadata.json", metadata)
    print(f"Exact curve fell inside the returned interval at {covered}/{len(points)} grid points.")
    print(f"Wrote validation results to {args.output_dir.resolve()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runners = {
        "gaussian-curve": _run_gaussian,
        "dpsgd-curve": _run_dpsgd_curve,
        "dpsgd-epsilon": _run_dpsgd_epsilon,
        "validate-gaussian": _run_validate_gaussian,
    }
    try:
        return runners[args.command](args)
    except OptionalDependencyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
