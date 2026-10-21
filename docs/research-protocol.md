# Reproducible benchmark protocol

This protocol is intended to prevent accidental or intentional apples-to-oranges comparisons.

## Required reporting

For every experiment, publish:

- the exact mechanism and adjacency/sampling assumptions;
- sampling probability, noise multiplier, number of steps, target delta, and error tolerances;
- library versions, Python version, platform, and command line;
- the full epsilon/delta bounds returned by each backend, not only a central estimate;
- wall-clock time, peak memory if measured, and the hardware/software environment;
- raw CSV/JSON output plus plotting code.

## Fair comparison checklist

1. Match the mechanism and sampling model. Poisson subsampling and fixed-size sampling are not interchangeable without justification.
2. Match all privacy parameters and the requested target precision.
3. Compare certified upper bounds when the task is to guarantee a privacy budget; do not compare one method's estimate with another method's upper bound as if they were equivalent.
4. Separate algorithmic runtime from setup/compilation time and cache effects.
5. Repeat timing measurements, report a robust summary (e.g. median and interquartile range), and do not select only favorable cases.
6. Keep failed runs and numerical warnings in the results log. Do not silently drop inconvenient configurations.
7. Treat a curve that looks smoother or a central estimate that is closer on one grid as insufficient evidence of a better privacy guarantee.
8. For stochastic estimators, pre-register the random seed policy, oracle budget, repetitions, confidence intervals, and error metric.
9. Use the exact Gaussian formula as a correctness check only for the non-subsampled Gaussian mechanism; it is not a ground truth for Poisson-subsampled DP-SGD.

## Interpreting validation results

`validate-gaussian` compares the official PRV Accountant's reported interval with the analytic curve over a finite epsilon grid. The coverage fraction is a diagnostic, not a proof of a universal guarantee. Any point outside the returned interval should trigger investigation of assumptions, numerical settings, library versions, and implementation behavior.
