import pytest
import numpy as np
from src.nodes.popcorn_vacuum_density import (
    PopcornVacuumDensityNode,
    PopcornVacuumConfig,
    H0_EARLY_DEFAULT,
    H0_LOCAL_DEFAULT,
)


def test_hubble_tension_acceleration_scales():
    node = PopcornVacuumDensityNode()
    a0_early = node.compute_a0(H0_EARLY_DEFAULT)
    a0_local = node.compute_a0(H0_LOCAL_DEFAULT)

    # a0 should be approximately around 1.0e-10 to 1.3e-10 m/s^2
    assert 0.8e-10 < a0_early < 1.3e-10
    assert 0.9e-10 < a0_local < 1.4e-10
    assert a0_local > a0_early, "Local H0 tension must yield larger critical acceleration"


def test_popcorn_nucleation_limits():
    node = PopcornVacuumDensityNode()
    g_bar = np.array([1e-8, 1e-10, 1e-12])  # High, transition, and deep-vacuum regimes
    res = node.compute({"g_bar": g_bar})

    # In high-acceleration regime (g_bar = 1e-8), vacuum compensation should be minimal
    assert res["vacuum_nucleation_factor"][0] < 0.5

    # In deep-vacuum regime (g_bar = 1e-12), vacuum nucleation dominates
    assert res["vacuum_nucleation_factor"][2] > 5.0

    # Local bubble nucleation should provide slightly higher boost than early CMB scale
    assert np.all(res["g_pop_local"] >= res["g_pop_early"])


def test_missing_input_raises_error():
    node = PopcornVacuumDensityNode()
    with pytest.raises(ValueError):
        node.compute({})
