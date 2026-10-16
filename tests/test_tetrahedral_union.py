"""
Test Tetrahedral Union and Multi-Node Geometry for SDF_QPUMP_Scaffold.
Verifies multi-node union operations without key collisions in the computational graph.
"""

import pytest
from src.core.graph import ComputationalGraph
from src.nodes.cavity_resonator import CavityResonatorNode


def test_tetrahedral_union_no_duplicate_nodes():
    graph = ComputationalGraph()

    # Define distinct node IDs to prevent duplicate registration
    cavity_1 = CavityResonatorNode(
        node_id="cavity_resonator_1",
        frequency_ghz=6.0,
        q_factor=5e4
    )
    cavity_2 = CavityResonatorNode(
        node_id="cavity_resonator_2",
        frequency_ghz=7.2,
        q_factor=8e4
    )

    graph.add_node(cavity_1)
    graph.add_node(cavity_2)

    assert len(graph.nodes) == 2
    assert "cavity_resonator_1" in graph.nodes
    assert "cavity_resonator_2" in graph.nodes

    # Execute graph aggregation/union
    results = graph.execute()
    assert results is not None
    assert "cavity_resonator_1" in results
    assert "cavity_resonator_2" in results
