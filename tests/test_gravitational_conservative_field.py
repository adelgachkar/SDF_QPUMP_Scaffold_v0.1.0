import pytest
from src.nodes.gravitational_curvature import GravitationalCurvatureNode

def test_gravitational_curvature_flat_regime():
    node = GravitationalCurvatureNode(coupling_g=1.0)
    result = node.compute({"net_thrust": 0.0})
    assert result["curvature_regime"] == "asymptotically_flat"
    assert result["effective_acceleration"] == 0.0
    assert result["is_locally_curved"] is False

def test_gravitational_curvature_conservative_field():
    node = GravitationalCurvatureNode(coupling_g=1.0)
    thrusts = [0.02, 0.05, 0.1, 0.5, 1.0, 2.0]
    for thrust in thrusts:
        result = node.compute({"net_thrust": thrust})
        expected_acc = thrust * node.coupling_g
        assert abs(result["effective_acceleration"] - expected_acc) < 1e-12
        assert result["ricci_scalar_proxy"] == thrust * node.coupling_g
