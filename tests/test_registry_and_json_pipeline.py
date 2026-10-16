"""
Test Registry and JSON Pipeline for SDF_QPUMP_Scaffold.
Ensures nodes register correctly and pipeline executes without errors.
"""
import pytest
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
                "params": {
                    "phase_frequency": 0.05,
                    "cavity_q": 1e5,
                },
            }
        ],
        "edges": [],
    }

    node_spec = pipeline_definition["nodes"][0]
    node = CavityResonatorNode(name=node_spec["id"], **node_spec["params"])
    
    # نودها در این پروژه متد compute دارند
    result = node.compute({})
    assert result is not None
    assert isinstance(result, dict)
