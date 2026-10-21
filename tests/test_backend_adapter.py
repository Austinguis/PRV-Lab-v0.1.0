import sys
import types

import pytest

from prv_lab.backends import dpsgd_delta_curve, dpsgd_epsilon


class FakeSubsampledGaussian:
    def __init__(self, *, noise_multiplier, sampling_probability):
        self.noise_multiplier = noise_multiplier
        self.sampling_probability = sampling_probability


class FakeGaussian:
    def __init__(self, *, noise_multiplier):
        self.noise_multiplier = noise_multiplier


class FakePRVAccountant:
    def __init__(self, *, prvs, max_self_compositions, eps_error, delta_error):
        self.prvs = prvs
        self.max_self_compositions = max_self_compositions
        self.eps_error = eps_error
        self.delta_error = delta_error

    def compute_delta(self, *, epsilon, num_self_compositions):
        assert num_self_compositions == self.max_self_compositions
        return max(0.0, 0.1 - epsilon * 0.01), 0.1 - epsilon * 0.01, 0.11 - epsilon * 0.01

    def compute_epsilon(self, *, delta, num_self_compositions):
        assert num_self_compositions == self.max_self_compositions
        return 1.0, 1.1, 1.2


def install_fake_prv(monkeypatch):
    fake = types.ModuleType("prv_accountant")
    fake.PRVAccountant = FakePRVAccountant
    fake.GaussianMechanism = FakeGaussian
    fake.PoissonSubsampledGaussianMechanism = FakeSubsampledGaussian
    monkeypatch.setitem(sys.modules, "prv_accountant", fake)


def test_dpsgd_delta_adapter_preserves_bounds(monkeypatch):
    install_fake_prv(monkeypatch)
    points = dpsgd_delta_curve(
        [0.0, 1.0],
        sampling_probability=0.01,
        noise_multiplier=1.2,
        steps=100,
        eps_error=0.01,
        delta_error=1e-8,
    )
    assert len(points) == 2
    assert points[0].delta_lower == pytest.approx(0.1)
    assert points[1].delta_estimate == pytest.approx(0.09)
    assert points[1].delta_upper == pytest.approx(0.10)


def test_dpsgd_epsilon_adapter_returns_all_three_values(monkeypatch):
    install_fake_prv(monkeypatch)
    result = dpsgd_epsilon(
        delta=1e-5,
        sampling_probability=0.01,
        noise_multiplier=1.2,
        steps=100,
    )
    assert (result.epsilon_lower, result.epsilon_estimate, result.epsilon_upper) == (1.0, 1.1, 1.2)
