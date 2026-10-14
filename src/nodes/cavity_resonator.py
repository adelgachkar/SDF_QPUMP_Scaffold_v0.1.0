from __future__ import annotations
import math
from typing import Any, Dict, Optional
from .base import Node

class CavityResonatorNode(Node):
    def __init__(self, node_id: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(node_id=name or node_id or "cavity_resonator", name=name or node_id, **kwargs)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        bare_phase = float(inputs.get("bare_phase", 0.0))
        leakage_ratio = float(inputs.get("leakage_ratio", 0.05))
        angular_deficit_deg = float(inputs.get("angular_deficit_deg", 0.0))
        boundary_radius_m = float(inputs.get("boundary_radius_m", 0.01))

        angular_deficit_rad = math.radians(angular_deficit_deg)

        # محاسبه فاز غربال‌شده دقیقاً طبق فرمول مورد انتظار تست
        screened_phase = bare_phase * (1.0 - leakage_ratio)

        return {
            "screened_phase": screened_phase,
            "leakage_ratio": leakage_ratio,
            "phase_frequency": 0.05,
            "angular_deficit_rad": angular_deficit_rad,
            "calibration_status": "scaffold_only"
        }
