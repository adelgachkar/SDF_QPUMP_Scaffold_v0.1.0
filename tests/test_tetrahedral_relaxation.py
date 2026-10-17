"""
Tests for TetrahedralRelaxationNode dynamic stress behavior.
"""

import math
import pytest
from src.nodes.tetrahedral_cluster import FiveTetrahedralUnionNode
from src.nodes.tetrahedral_relaxation import TetrahedralRelaxationNode


def test_tetrahedral_relaxation_isolated_decay():
    """Verifies that dynamic stress decays exponentially toward target static stress."""
    gamma = 0.5
    dt = 0.1
    relax_node = TetrahedralRelaxationNode(
        node_id="test_relax",
        config={"relaxation_rate": gamma, "dt": dt}
    )

    target_stress = 0.05
    initial_stress = 0.20
    n_steps = 120

    out = relax_node.execute({
        "frustration_stress": target_stress,
        "initial_stress": initial_stress,
        "n_steps": n_steps
    })

    assert "dynamic_stress" in out
    assert "stress_trace" in out
    assert len(out["stress_trace"]) == n_steps + 1

    expected_final = target_stress + (initial_stress - target_stress) * math.exp(-gamma * (n_steps * dt))
    assert math.isclose(out["dynamic_stress"], expected_final, abs_tol=1e-7)

    assert math.isclose(out["dynamic_stress"], target_stress, abs_tol=1e-3)
    assert out["equilibrium_ratio"] > 0.99


def test_tetrahedral_relaxation_validation_error():
    """Ensures node raises ValueError with standard node_id prefix on missing input."""
    node = TetrahedralRelaxationNode(node_id="relax_err_test")
    with pytest.raises(ValueError) as excinfo:
        node.execute({})
    assert "[relax_err_test]" in str(excinfo.value)


def test_tetrahedral_union_to_relaxation_chain():
    """End-to-End integration test connecting FiveTetrahedralUnionNode directly to Relaxation."""
    union = FiveTetrahedralUnionNode(node_id="union_step", config={"coupling_efficiency": 0.95})
    relax = TetrahedralRelaxationNode(node_id="relax_step", config={"relaxation_rate": 0.2})

    phases = [0.0, 0.1, 0.2, 0.3, 0.4]
    union_out = union.execute({"cell_phases": phases})
    static_stress = union_out["frustration_stress"]

    relax_out = relax.execute({
        "frustration_stress": static_stress,
        "initial_stress": static_stress * 2.0,
        "n_steps": 10
    })

    assert relax_out["target_stress"] == static_stress
    assert relax_out["dynamic_stress"] < (static_stress * 2.0)
    assert relax_out["residual_frustration"] < abs(static_stress)
