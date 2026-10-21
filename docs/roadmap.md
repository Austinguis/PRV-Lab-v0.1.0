# Roadmap

## v0.1 — Reproducible core

- [x] Exact non-subsampled Gaussian privacy curve and inverse.
- [x] Optional adapter for Microsoft's PRV Accountant.
- [x] CSV, PNG, and run metadata output.
- [x] Unit tests and GitHub Actions CI.
- [x] Research protocol and project governance files.

## v0.2 — Benchmark adapters

- [ ] Add a separately tested RDP backend (e.g. through a maintained library).
- [ ] Add benchmark tables with matched mechanisms, error targets, runtime, and memory.
- [ ] Add environment lock files and a small, versioned benchmark fixture.
- [ ] Add CI coverage for supported Python versions and dependency combinations.

## v0.3 — Research diagnostics

- [ ] Add automated curve monotonicity and interval-consistency diagnostics.
- [ ] Add repeatable timing harness with warm-up, repeated runs, and summary statistics.
- [ ] Add a validated adapter for the Wang importance-sampling method, subject to license and API review.
- [ ] Add a validated adapter for the KJPH Fourier accountant, subject to license and API review.

## Research contributions (exploratory; not claims)

- [ ] Investigate precision allocation across epsilon regions under a fixed runtime budget.
- [ ] Investigate automatic failure diagnostics for negative mass, truncation, and interval violations.
- [ ] Investigate whether benchmark metadata predicts when each accountant is efficient.

No item above should be described as a novel algorithm or performance improvement until supported by a clear theorem or reproducible experiments.
