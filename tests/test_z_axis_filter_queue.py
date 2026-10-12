"""
Unit tests for ZAxisFilterQueueNode in Q-PUMP pipeline.
"""

import numpy as np
import pytest

from src.nodes.z_axis_filter_queue import ZAxisFilterQueueNode


def test_z_axis_filter_queue_basic_execution():
    node = ZAxisFilterQueueNode(node_id="test_filter_queue")
    inputs = {
        "intensity": 1.5,
        "screened_phase": 0.128,
        "r_wall": 0.8,
    }
    result = node.execute(inputs)

    assert "filtered_modes" in result
    assert "snr_profile" in result
    assert "z_queue_state" in result
    assert "effective_axial_flux" in result
    assert result["resonance_gain"] > 1.0
    assert result["effective_axial_flux"] > 0.0


def test_z_axis_filter_queue_array_inputs():
    node = ZAxisFilterQueueNode(
        node_id="test_filter_array",
        config={"queue_capacity": 3, "alpha_growth": 0.3},
    )
    inputs = {
        "jet_flux": [0.5, 1.2, 2.0, 0.8],
        "screened_phase": [0.1, 0.2, 0.3, 0.4],
        "z_steps": np.linspace(0.0, 2.0, 20),
        "r_wall": 0.9,
    }
    result = node.execute(inputs)

    assert len(result["filtered_modes"]) == 4
    assert len(result["snr_profile"]) == 20
    assert len(result["z_queue_state"]) == 3
    # Check queue ordering descending
    amps = [item["amplitude"] for item in result["z_queue_state"]]
    assert amps == sorted(amps, reverse=True)
