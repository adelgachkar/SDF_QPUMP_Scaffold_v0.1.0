"""Tests for ResonantSpinonZeroModeNode based on Chen & Lado (2020)."""

import numpy as np
import pytest
from src.nodes.resonant_spinon_zero_mode import ResonantSpinonZeroModeNode


def test_node_instantiation():
    node = ResonantSpinonZeroModeNode(node_id="test_spinon_1")
    assert node.node_id == "test_spinon_1"
    assert node.config["hopping_t"] == 1.0
    assert node.config["default_eta"] == 0.05


def test_zero_bias_peak_presence():
    node = ResonantSpinonZeroModeNode()
    res = node.compute({"impurity_density": 0.01, "distance_bonds": 1})

    assert "resonant_ldos_zero" in res
    assert "zero_bias_intensity" in res
    assert res["resonant_ldos_zero"] > 0.0
    assert res["zero_bias_intensity"] > 0.0

    s_vals = res["spectral_density"]
    mid_idx = len(s_vals) // 2
    assert s_vals[mid_idx] > s_vals[0]


def test_zero_mode_quenching_with_impurity_density():
    node = ResonantSpinonZeroModeNode()
    res_isolated = node.compute({"impurity_density": 0.01})
    res_dense = node.compute({"impurity_density": 0.30})

    assert res_isolated["zero_mode_persistence"] > res_dense["zero_mode_persistence"]
    assert res_dense["zero_mode_persistence"] < 0.5


def test_sublattice_parity_odd_vs_even():
    node = ResonantSpinonZeroModeNode()
    res_odd = node.compute({"distance_bonds": 1, "impurity_density": 0.02})
    res_even = node.compute({"distance_bonds": 2, "impurity_density": 0.02})

    assert res_odd["resonant_ldos_zero"] > res_even["resonant_ldos_zero"]


def test_cavity_coupling_injection():
    node = ResonantSpinonZeroModeNode()
    res_low = node.compute({"cavity_coupling": 0.5})
    res_high = node.compute({"cavity_coupling": 2.0})

    assert res_high["effective_vacuum_injection"] > res_low["effective_vacuum_injection"]
