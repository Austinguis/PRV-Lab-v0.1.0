# PRV-Lab

**Reproducible differential-privacy accounting experiments, reference curves, and numerical diagnostics.**

[中文说明](README_zh.md) · [Research protocol](docs/research-protocol.md) · [Roadmap](docs/roadmap.md) · [Repository](https://github.com/Austinguis/PRV-Lab-v0.1.0)

PRV-Lab provides a small Python toolkit for generating privacy curves, inspecting numerical bounds, and exporting experiment data with the parameters and environment used to produce it. Version 0.1.0 includes an analytic Gaussian reference and an optional adapter to Microsoft's [PRV Accountant](https://github.com/microsoft/prv_accountant).

## Features

- Analytic `delta(epsilon)` curves for identical, independently composed, non-subsampled Gaussian mechanisms.
- Numerical inversion of the analytic curve to obtain epsilon at a target delta through the Python API.
- An optional PRV Accountant adapter for Poisson-subsampled Gaussian DP-SGD, preserving lower bounds, estimates, and upper bounds.
- A finite-grid comparison of the PRV backend with the analytic Gaussian reference.
- CSV data, PNG figures, and JSON run metadata.
- Unit tests and GitHub Actions workflows for testing and building distributions.

This is an initial research-tooling release. The current implementation does not introduce a new privacy accountant. The analytic Gaussian reference applies to non-subsampled mechanisms and must not be used as a replacement for subsampled DP-SGD accounting.

## Installation

Python 3.10 or later is required. Git is needed only for the clone method; alternatively, download the repository ZIP, extract it, and open a terminal in the folder containing `pyproject.toml`.

### Windows PowerShell

```powershell
git clone https://github.com/Austinguis/PRV-Lab-v0.1.0.git
cd PRV-Lab-v0.1.0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

If PowerShell blocks activation, use the environment's Python directly without changing your execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m prv_lab.cli --help
```

In that case, replace `prv-lab` in the examples below with `.\.venv\Scripts\python.exe -m prv_lab.cli`.

### macOS / Linux

```bash
git clone https://github.com/Austinguis/PRV-Lab-v0.1.0.git
cd PRV-Lab-v0.1.0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### Optional dependencies

Run these commands from the repository root using the virtual environment:

```bash
# Add the PRV Accountant backend for DP-SGD and validation commands.
python -m pip install -e ".[prv]"

# Add development tools for tests, linting, and distribution builds.
python -m pip install -e ".[dev]"
```

Both sets can be installed with `python -m pip install -e ".[dev,prv]"`. The default installation supports the analytic Gaussian reference without the PRV backend. These instructions install from this repository and do not assume a PyPI release exists.

## Quick start

The following commands are single lines that can be pasted into PowerShell or a Bash-compatible shell after activating the virtual environment.

### 1. Analytic Gaussian privacy curve

```bash
prv-lab gaussian-curve --noise-std 2.0 --sensitivity 1.0 --steps 100 --eps-max 5 --points 201 --output-dir results/gaussian-demo
```

Outputs:

- `gaussian_curve.csv`: epsilon and analytic delta values.
- `gaussian_curve.png`: a privacy curve figure.
- `run_metadata.json`: parameters, timestamp, and environment information.

For `k` identical independent compositions, sensitivity `Delta`, and per-step noise standard deviation `sigma`, the reference uses:

$$
\mu = \frac{\sqrt{k}\,\Delta}{\sigma}, \qquad
\delta(\epsilon) = \Phi\!\left(\frac{\mu}{2}-\frac{\epsilon}{\mu}\right)
- e^{\epsilon}\Phi\!\left(-\frac{\mu}{2}-\frac{\epsilon}{\mu}\right).
$$

Here, `Phi` is the standard normal cumulative distribution function. The formula is analytic; its implementation uses floating-point numerical evaluation.

To invert the curve from Python:

```python
from prv_lab.curves import gaussian_epsilon

epsilon = gaussian_epsilon(
    delta=1e-5,
    noise_std=2.0,
    sensitivity=1.0,
    steps=100,
)
print(epsilon)
```

### 2. DP-SGD privacy curve

Install the optional PRV backend first.

```bash
prv-lab dpsgd-curve --sampling-probability 0.01 --noise-multiplier 1.2 --steps 1000 --eps-max 8 --points 201 --eps-error 0.01 --delta-error 1e-8 --output-dir results/dpsgd-demo
```

This writes `dpsgd_curve.csv`, `dpsgd_curve.png`, and `run_metadata.json`. CSV columns preserve the backend's delta lower bound, estimate, and upper bound.

### 3. Epsilon bounds at a target delta

```bash
prv-lab dpsgd-epsilon --sampling-probability 0.01 --noise-multiplier 1.2 --steps 1000 --delta 1e-5 --eps-error 0.01 --output-dir results/dpsgd-epsilon
```

This writes `dpsgd_epsilon.csv` and `run_metadata.json`, and prints epsilon lower, estimated, and upper values.

### 4. Compare the PRV backend with the Gaussian reference

```bash
prv-lab validate-gaussian --noise-std 2.0 --steps 100 --eps-max 5 --points 101 --output-dir results/gaussian-validation
```

This command compares a non-subsampled Gaussian mechanism across the two implementations. Outputs include `gaussian_validation.csv`, `gaussian_validation.png`, and `run_metadata.json`, with a diagnostic of how many grid points fall inside the reported interval. A finite-grid check does not establish correctness for every parameter setting.

## Development and verification

From an activated virtual environment in the repository root:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m build
```

The CI workflow is configured for Python 3.10, 3.11, and 3.12. The default test setup does not install the real PRV backend; adapter tests use a fake backend, and a separate test checks the missing-dependency message. Passing these tests alone does not validate the real backend's numerical behavior.

The release workflow builds distribution artifacts when a `v*` tag is pushed or when manually triggered. It does not automatically publish a package to PyPI or create a GitHub Release. Maintainer instructions are in [PUBLISHING.md](PUBLISHING.md).

## Research protocol and scope

Read the [research protocol](docs/research-protocol.md) before interpreting comparisons or reporting experimental conclusions.

- Match the mechanism, adjacency relation, sampling model, noise scale, composition count, and error targets when comparing accountants.
- Use valid upper bounds for privacy guarantees; an estimate and an upper bound are different quantities.
- Record hardware, dependency versions, precision settings, error tolerances, and failed runs for reproducible comparisons.
- Validate the assumptions of the complete analysis before using outputs as privacy guarantees.

Future adapters and benchmark work are tracked in the [roadmap](docs/roadmap.md). Planned features are not claims about the current release.

## Contributing and security

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. Reports should include a minimal reproduction, exact command, and environment information. Use the [issue tracker](https://github.com/Austinguis/PRV-Lab-v0.1.0/issues) for ordinary bugs and feature requests.

For vulnerabilities or numerical issues that could invalidate privacy guarantees, follow [SECURITY.md](SECURITY.md). Remove credentials, private datasets, and identifying information from public reports.

## Citation

Use [CITATION.cff](CITATION.cff) to cite the software, and identify the version or commit used in your experiments. Cite the underlying accounting research and libraries when their methods are used.

## License

PRV-Lab is distributed under the [MIT License](LICENSE). Dependencies retain their own licenses.

## References

- Gopi, Lee, and Wutschitz, [Numerical Composition of Differential Privacy](https://arxiv.org/abs/2106.02848), NeurIPS 2021.
- Microsoft [PRV Accountant](https://github.com/microsoft/prv_accountant).
