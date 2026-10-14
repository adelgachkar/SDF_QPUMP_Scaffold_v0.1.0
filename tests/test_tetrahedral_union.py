"""
test_tetrahedral_union.py - آزمون‌های صحه‌گذاری هم‌جوشی تتراهدرال و اتصال ۵ سلول
"""

from __future__ import annotations
import math
import pytest

from src.core import Graph
from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.tetrahedral_cluster import TetrahedralClusterNode, FiveTetrahedralUnionNode


def test_tetrahedral_cluster_isolated_constructive():
    """تست تداخل کاملاً سازنده ۴ کاواک هم‌فاز در تقارن تتراهدرال."""
    node = TetrahedralClusterNode(node_id="tet_cluster_1", config={"coupling_strength": 0.25})
    out = node.compute({"phases": [0.5, 0.5, 0.5, 0.5]})

    assert math.isclose(out["coherence_index"], 1.0, abs_tol=1e-5)
    assert math.isclose(out["core_amplitude"], 1.0, abs_tol=1e-5)
    assert math.isclose(out["core_phase"], 0.5, abs_tol=1e-5)
    assert math.isclose(out["angular_deficit_rad"], 0.0, abs_tol=1e-7)
    assert out["cell_count"] == 4


def test_tetrahedral_cluster_destructive_interference():
    """تست افت همدوسی در فازهای غیرهم‌راستا و تداخل متقارن متضاد."""
    node = TetrahedralClusterNode(node_id="tet_cluster_2", config={"coupling_strength": 0.25})
    out = node.compute({"phases": [0.0, math.pi, 0.0, math.pi]})

    assert math.isclose(out["core_amplitude"], 0.0, abs_tol=1e-6)
    assert math.isclose(out["coherence_index"], 0.0, abs_tol=1e-6)
    assert out["angular_deficit_rad"] > 0.0


def test_five_tetrahedral_union_geometric_gap():
    """تست کسری زاویه‌ای ذاتی هندسه ۵ چهاروجهی منتظم (حدود 7.356 درجه)."""
    node = FiveTetrahedralUnionNode(node_id="union_5cell")
    expected_gap_deg = 360.0 - (5.0 * math.degrees(math.acos(1.0 / 3.0)))
    expected_gap_rad = math.radians(expected_gap_deg)

    out = node.compute({"cell_phases": [0.1, 0.1, 0.1, 0.1, 0.1]})

    assert math.isclose(out["geometric_gap_rad"], expected_gap_rad, rel_tol=1e-5)
    assert out["cells_unified"] == 5
    assert out["union_amplitude"] > 0.0
    assert 0.0 <= out["global_coherence"] <= 1.0


def test_five_tetrahedral_union_requires_five_cells():
    """اعتبارسنجی ورودی: نود باید دقیقاً ۵ سلول ورودی دریافت کند."""
    node = FiveTetrahedralUnionNode(node_id="union_strict")
    with pytest.raises(ValueError):
        node.compute({"cell_phases": [0.1, 0.2, 0.3]})


def test_end_to_end_cavity_to_union_dag():
    """تست اجرای سناریوی تجمیع ۵ کاواک تشدیدگر درون نود اتحاد پنج سلولی."""
    graph = Graph()

    for i in range(1, 6):
        c_node = CavityResonatorNode(node_id=f"cavity_{i}", config={"leakage_ratio": 0.1})
        graph.add_node(c_node)

    screened_phases = []
    for i in range(1, 6):
        c_out = graph.nodes[f"cavity_{i}"].compute({"bare_phase": 0.15 * i, "angular_deficit_deg": 4.0})
        screened_phases.append(c_out["screened_phase"])

    union_node = FiveTetrahedralUnionNode(node_id="union_core", config={"coupling_efficiency": 0.95})
    union_out = union_node.compute({"cell_phases": screened_phases})

    assert union_out["cells_unified"] == 5
    assert union_out["union_amplitude"] > 0.0
    assert union_out["frustration_stress"] >= 0.0
