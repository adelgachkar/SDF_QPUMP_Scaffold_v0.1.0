"""
test_tetrahedral_pipeline_e2e.py - آزمون جریان داده انتها-به-انتها (E2E)
اتصال ابرساختار تتراهدرال 5-سلولی به RadialPropagationNode و ZAxisFilterQueueNode
"""

from __future__ import annotations
import math
import numpy as np
import pytest

from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.tetrahedral_cluster import FiveTetrahedralUnionNode
from src.nodes.radial_propagation import RadialPropagationNode
from src.nodes.z_axis_filter_queue import ZAxisFilterQueueNode


def test_tetrahedral_to_radial_and_z_filter_e2e():
    """
    تست زنجیره کامل:
    5 کاواک تشدیدگر -> اتحاد 5-تتراهدرال -> انتشار شعاعی -> فیلتر پالس محور Z
    """
    # 1. پنج کاواک تشدیدگر
    resonator = CavityResonatorNode(node_id="cav_unit", config={"leakage_ratio": 0.05})
    cell_phases = []
    for i in range(1, 6):
        res_out = resonator.execute({"bare_phase": 0.12 * i, "angular_deficit_deg": 3.6})
        cell_phases.append(res_out["screened_phase"])

    assert len(cell_phases) == 5

    # 2. اتحاد 5-تتراهدرال
    union_node = FiveTetrahedralUnionNode(node_id="union_5cell", config={"coupling_efficiency": 0.96})
    union_out = union_node.execute({"cell_phases": cell_phases})

    assert union_out["cells_unified"] == 5
    assert union_out["union_amplitude"] > 0.0

    # 3. انتشار شعاعی موج برآمده از هسته تتراهدرال
    radial_node = RadialPropagationNode(
        node_id="radial_prop",
        delta_r=0.25,
        k_radial=2.0,
        alpha_div=0.5,
    )
    packet_in = {
        "amplitude": union_out["union_amplitude"],
        "phase": union_out["union_phase"],
        "r": 1.0,
    }
    radial_out = radial_node.execute({"packet": packet_in})

    assert radial_out["packet_count"] == 1
    propagated_pkt = radial_out["propagated_packets"][0]
    assert propagated_pkt["radial_propagated"] is True
    assert propagated_pkt["r"] > 1.0

    # 4. فیلتر صف محور Z بر اساس شدت میدان عبوری و فاز نهایی
    z_filter = ZAxisFilterQueueNode(
        node_id="z_filter_final",
        config={"queue_capacity": 4},
    )
    z_inputs = {
        "intensity": propagated_pkt["amplitude"] ** 2,
        "screened_phase": propagated_pkt["phase"],
        "r_wall": 0.85,
    }
    z_out = z_filter.execute(z_inputs)

    assert "filtered_modes" in z_out
    assert "snr_profile" in z_out
    assert "z_queue_state" in z_out
    assert z_out["resonance_gain"] > 1.0
    assert z_out["effective_axial_flux"] > 0.0


def test_tetrahedral_e2e_coherence_under_frustration():
    """بررسی رفتار تنش ناکامی هندسی در شرایط فازهای آشفته."""
    union_node = FiveTetrahedralUnionNode(node_id="union_stress_check")

    out_balanced = union_node.execute({"cell_phases": [0.1, 0.1, 0.1, 0.1, 0.1]})
    out_dispersed = union_node.execute({"cell_phases": [0.0, 1.2, 2.5, -1.0, 0.8]})

    assert out_dispersed["frustration_stress"] > out_balanced["frustration_stress"]
