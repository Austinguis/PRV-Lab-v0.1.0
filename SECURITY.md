# Security Policy

## Scope

PRV-Lab is research software for privacy-accounting experiments. Incorrect accounting can lead to invalid privacy claims, so numerical correctness issues should be reported responsibly.

## Reporting a vulnerability

Please do not publish exploitable details, credentials, or sensitive data in a public issue. Until a private security contact is configured, use GitHub's private vulnerability reporting feature if it is enabled for the repository. Otherwise contact the maintainers through a verified public contact channel and include a minimal reproduction without private data.

## What to include

- affected version/commit;
- Python and dependency versions;
- minimal command or code sample;
- expected versus observed behavior;
- whether the issue could produce an invalidly optimistic privacy bound.

Do not assume that an output is safe to use as a privacy guarantee until the issue is understood and resolved.
