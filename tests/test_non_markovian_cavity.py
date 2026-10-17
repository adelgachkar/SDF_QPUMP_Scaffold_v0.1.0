"""
Unit tests for the exact Non-Markovian Cavity Resonator Node.
Validates:
  1. Node instantiation and interface structure
  2. Quantum Zeno regime (gamma(0) suppressed at t -> 0)
  3. Coherence and information backflow (gamma(t) < 0) in strong-coupling sub-Ohmic regime
  4. Monotonic exponential decay in the weak-coupling Markovian limit
"""

import numpy as np
import pytest

from src.nodes.non_markovian_cavity import NonMarkovianCavityNode


def test_node_initialization_and_keys():
    """Validates output dictionary schema and parameter propagation."""
    node = NonMarkovianCavityNode(
        omega_r=5.0,
        eta=0.05,
        cutoff_wc=20.0,
        spectral_s=1.0,
        t_max=2.0,
        n_steps=100,
    )
    result = node.compute()

    required_keys = [
        "time_grid",
        "green_function_u",
        "population_trace",
        "final_population",
        "gamma_t",
        "delta_omega_t",
        "coherence_factor",
        "has_coherence_backflow",
        "non_markovianity_measure",
        "zeno_initial_decay_rate",
    ]
    for key in required_keys:
        assert key in result, f"Missing output key: {key}"

    assert len(result["time_grid"]) == 100
    assert len(result["green_function_u"]) == 100
    assert np.isclose(np.abs(result["green_function_u"][0]), 1.0, atol=1e-5)


def test_zeno_regime_short_time():
    """
    Quantum Zeno effect: In structured environments, the initial decay rate
    starts strongly suppressed: gamma(0) -> 0, leading to a parabolic short-time
    decay (1 - C * t^2) rather than Markovian linear decay (1 - gamma * t).
    Accounting for finite grid step discretization (dt ~ 0.005), gamma(0)
    remains well below 0.03 and significantly smaller than the peak rate.
    """
    node = NonMarkovianCavityNode(
        omega_r=2.0,
        eta=0.1,
        cutoff_wc=10.0,
        spectral_s=1.0,
        t_max=1.0,
        n_steps=200,
    )
    result = node.compute()

    gamma = result["gamma_t"]
    # Zeno regime: initial rate is strongly suppressed near t=0
    assert abs(gamma[0]) < 0.03, f"Expected suppressed gamma(0), got {gamma[0]}"
    # Rate builds up over reservoir correlation timescale
    assert np.max(gamma) > 3.0 * gamma[0], "Decay rate did not build up over time from Zeno suppression."


def test_sub_ohmic_strong_coupling_backflow():
    """
    Validates coherence/information backflow:
    Under strong reservoir coupling (eta=2.5, sub-Ohmic s=0.5), the effective
    decay rate gamma(t) becomes negative, yielding a positive non-Markovianity measure.
    """
    node = NonMarkovianCavityNode(
        omega_r=1.0,
        eta=2.5,
        cutoff_wc=4.0,
        spectral_s=0.5,  # Sub-Ohmic regime induces structured memory
        t_max=6.0,
        n_steps=400,
    )
    result = node.compute()

    gamma = result["gamma_t"]
    has_negative_gamma = np.any(gamma < -0.01)

    assert has_negative_gamma, "Failed to capture negative gamma(t) in strong-coupling regime."
    assert result["has_coherence_backflow"] is True
    assert result["non_markovianity_measure"] > 0.0


def test_monotonic_decay_weak_coupling_limit():
    """
    In the weak-coupling Ohmic regime (Markovian limit), decay is strictly
    monotonic with negligible backflow.
    """
    node = NonMarkovianCavityNode(
        omega_r=5.0,
        eta=0.01,  # Weak coupling
        cutoff_wc=30.0,
        spectral_s=1.0,  # Pure Ohmic
        t_max=5.0,
        n_steps=250,
    )
    result = node.compute()

    pop = result["population_trace"]
    # Monotonicity test: population never increases significantly
    diffs = np.diff(pop)
    assert np.all(diffs <= 1e-4), "Markovian regime exhibited unphysical population growth."
    assert result["non_markovianity_measure"] < 1e-3
