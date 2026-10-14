"""
tetrahedral_cluster.py - نودهای هم‌جوشی تتراهدرال و ابرساختار اتحاد ۵ سلول (Five-Tetrahedral Union)
طراحی شده برای فریم‌ورک SDF_QPUMP_Scaffold
"""

from __future__ import annotations
from typing import Dict, Any, List
import math
import numpy as np

try:
    from src.nodes.base import BaseNode
except ImportError:
    from qpump.nodes.base import BaseNode


class TetrahedralClusterNode(BaseNode):
    """
    نود هم‌جوشی تتراهدرال (T_d symmetry):
    محاسبه تداخل و برآیند فازورهای ۴ کاواک متقارن، شاخص همدوسی و انحراف فاز.
    """

    def __init__(self, node_id: str, label: str | None = None, config: Dict[str, Any] | None = None):
        super().__init__(node_id=node_id, label=label, config=config)
        self.coupling_strength = float(self.config.get("coupling_strength", 0.25))
        # زاویه مشخصه چهاروجهی منتظم: arccos(-1/3) ~ 109.471 deg
        self.characteristic_angle_rad = math.acos(-1.0 / 3.0)

    @property
    def required_inputs(self) -> List[str]:
        return ["phases"]

    @property
    def outputs(self) -> List[str]:
        return [
            "core_amplitude",
            "core_phase",
            "coherence_index",
            "angular_deficit_rad",
            "cell_count",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        phases = inputs.get("phases", [])
        if not phases:
            phases = [inputs.get(f"phase_{i}", 0.0) for i in range(1, 5) if f"phase_{i}" in inputs]

        if not phases:
            raise ValueError(f"[{self.node_id}] Inputs must contain non-empty 'phases'.")

        phases_arr = np.array(phases, dtype=np.float64)
        n_cells = len(phases_arr)

        amplitudes = inputs.get("amplitudes", [1.0] * n_cells)
        amp_arr = np.array(amplitudes, dtype=np.float64)

        # برهم‌نهی فازوری مدهای الکترومغناطیسی هسته
        phasors = amp_arr * np.exp(1j * phases_arr)
        fused_field = np.sum(phasors) * self.coupling_strength

        core_amp = float(np.abs(fused_field))
        core_phase = float(np.angle(fused_field))

        # شاخص همدوسی کوانتومی (میزان سازندگی تداخل نسبت به سقف نظری)
        max_possible_amp = np.sum(amp_arr) * self.coupling_strength
        coherence = float(core_amp / max_possible_amp) if max_possible_amp > 1e-12 else 0.0

        phase_std = float(np.std(phases_arr))
        deficit = float(phase_std * math.sin(self.characteristic_angle_rad / 2.0))

        return {
            "core_amplitude": core_amp,
            "core_phase": core_phase,
            "coherence_index": coherence,
            "angular_deficit_rad": deficit,
            "cell_count": n_cells,
        }


class FiveTetrahedralUnionNode(BaseNode):
    """
    ابرساختار اتحاد ۵ سلول تتراهدرال (Five-Tetrahedral Union):
    اتصال ۵ چهاروجهی حول یال مشترک دارای نقص زاویه‌ای بسته شدن هندسی است:
    360 - 5 * arccos(1/3) = 7.3561 deg (~0.128388 rad)
    """

    # نقص زاویه‌ای فضایی بر حسب رادیان
    GEOMETRIC_GAP_RAD: float = math.radians(360.0 - (5.0 * math.degrees(math.acos(1.0 / 3.0))))

    def __init__(self, node_id: str, label: str | None = None, config: Dict[str, Any] | None = None):
        super().__init__(node_id=node_id, label=label, config=config)
        self.coupling_efficiency = float(self.config.get("coupling_efficiency", 0.95))

    @property
    def required_inputs(self) -> List[str]:
        return ["cell_phases"]

    @property
    def outputs(self) -> List[str]:
        return [
            "union_amplitude",
            "union_phase",
            "geometric_gap_rad",
            "frustration_stress",
            "global_coherence",
            "cells_unified",
        ]

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        cell_phases = inputs.get("cell_phases", [])
        if len(cell_phases) != 5:
            raise ValueError(f"[{self.node_id}] FiveTetrahedralUnionNode strictly requires 5 cell phases.")

        phases_arr = np.array(cell_phases, dtype=np.float64)

        # اعمال شیفت تصحیح کسری زاویه‌ای به ازای هر سلول (Phase Frustration Relaxation)
        gap_correction_step = self.GEOMETRIC_GAP_RAD / 5.0
        adjusted_phases = phases_arr + np.array([i * gap_correction_step for i in range(5)])

        phasors = np.exp(1j * adjusted_phases)
        composite_field = np.sum(phasors) * (self.coupling_efficiency / 5.0)

        union_amp = float(np.abs(composite_field))
        union_phase = float(np.angle(composite_field))
        coherence = float(union_amp / self.coupling_efficiency)

        frustration_stress = float(abs(np.std(adjusted_phases) * self.GEOMETRIC_GAP_RAD))

        return {
            "union_amplitude": union_amp,
            "union_phase": union_phase,
            "geometric_gap_rad": float(self.GEOMETRIC_GAP_RAD),
            "frustration_stress": frustration_stress,
            "global_coherence": coherence,
            "cells_unified": 5,
        }
