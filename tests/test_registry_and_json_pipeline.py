"""Tests for node registry completeness and JSON pipeline configuration loader."""

from pathlib import Path
import pytest

from src.registry import (
    registered_types,
    create_node,
    load_graph_from_json,
    load_graph_from_dict,
)
from src.core import Graph


def test_all_expected_nodes_registered():
    """Verify all built-in domain nodes are registered in the global registry."""
    reg = registered_types()
    expected_types = [
        "cavity_resonator",
        "berry_torque_bridge",
        "peristaltic_pump",
        "boundary_stress_integrator",
        "gravitational_curvature",
        "effective_metric_source",
        "quantum_backreaction",
        "radial_propagation",
        "optical_phase_step",
        "z_axis_filter_queue",
        "tetrahedral_cluster",
        "five_tetrahedral_union",
    ]
    for ntype in expected_types:
        assert ntype in reg, f"Missing registered node type: {ntype}"


def test_create_nodes_from_registry():
    """Verify instantiation via create_node for newly integrated nodes."""
    cluster = create_node("tetrahedral_cluster", name="cluster_0")
    assert cluster.name == "cluster_0"

    union = create_node("five_tetrahedral_union", name="union_0")
    assert union.name == "union_0"

    z_filter = create_node("z_axis_filter_queue", name="z_filter_0")
    assert z_filter.name == "z_filter_0"


def test_load_graph_from_example_json():
    """Verify pipeline_qpump_example.json can be loaded into an executable Graph."""
    config_path = Path("config") / "pipeline_qpump_example.json"
    if not config_path.is_file():
        pytest.skip("config/pipeline_qpump_example.json not found")

    graph = load_graph_from_json(config_path)
    assert isinstance(graph, Graph)
    assert "cavity" in graph.nodes
    assert "pump" in graph.nodes
    assert "bridge" in graph.nodes
    assert "stress" in graph.nodes
    assert "metric" in graph.nodes

    # Execute a simple deterministic run
    initial_inputs = {
        "cavity": {"drive_phase": 0.5, "delta_theta": 0.05}
    }
    results = graph.run(initial_inputs)
    assert "metric" in results
    assert "effective_metric_perturbation" in results["metric"]
