"""
Test Registry and JSON Pipeline for SDF_QPUMP_Scaffold.
Ensures nodes register correctly and DAG pipeline executes without missing node keys.
"""

import json
import pytest
from src.core.graph import ComputationalGraph
from src.core.registry import NodeRegistry
from src.nodes.cavity_resonator import CavityResonatorNode


def test_registry_registration():
    registry = NodeRegistry()
    registry.register("cavity_resonator", CavityResonatorNode)
    assert "cavity_resonator" in registry.list_nodes()
    node_cls = registry.get("cavity_resonator")
    assert node_cls is CavityResonatorNode


def test_json_pipeline_execution():
    pipeline_definition = {
        "nodes": [
            {
                "id": "cavity_resonator",
                "type": "cavity_resonator",
                "params": {"frequency_ghz": 6.5, "q_factor": 1e5}
            }
        ],
        "edges": []
    }

    graph = ComputationalGraph()
    for node_spec in pipeline_definition["nodes"]:
        node = CavityResonatorNode(
            node_id=node_spec["id"],
            **node_spec["params"]
        )
        graph.add_node(node)

    assert "cavity_resonator" in graph.nodes
    result = graph.execute()
    assert result is not None
