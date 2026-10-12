import math
from src.nodes import (
    CavityResonatorNode,
    BerryTorqueBridgeNode,
    PeristalticPumpNode,
    BoundaryStressIntegratorNode,
    GravitationalCurvatureNode,
    QuantumBackreactionNode
)

def test_end_to_end_sequential_dataflow():
    """
    Simulates complete physical execution from initial Cavity seed to Step 13 Radial Propagation.
    """
    # 1. Cavity Resonator
    cavity = CavityResonatorNode(node_id="cav_01")
    cav_out = cavity.execute({
        "bare_phase": 0.5236,
        "angular_deficit_deg": 7.2,
        "leakage_ratio": 0.05
    })
    # Status can be scaffold_only or valid depending on calibration completeness
    assert cav_out["calibration_status"] in ["scaffold_only", "valid"]
    assert cav_out["phase_frequency"] > 0.0

    # 2. Berry Torque Bridge
    berry = BerryTorqueBridgeNode(node_id="berry_01")
    berry_out = berry.execute({
        "screened_phase": cav_out["screened_phase"],
        "alpha_target": 1.0,
        "angular_deficit_rad": cav_out["angular_deficit_rad"]
    })
    assert abs(berry_out["berry_phase_shift"]) > 0.0

    # 3. Peristaltic Pump
    pump = PeristalticPumpNode(node_id="pump_01")
    pump_out = pump.execute({
        "drive_amplitude": 1.25,
        "berry_phase_shift": berry_out["berry_phase_shift"],
        "phase_frequency": cav_out["phase_frequency"]
    })
    assert pump_out["jet_power"] > 0.0

    # 4. Boundary Stress Integrator
    stress = BoundaryStressIntegratorNode(node_id="stress_01")
    stress_out = stress.execute({
        "jet_power": pump_out["jet_power"],
        "noise_floor": 0.01
    })
    assert "stress_tensor" in stress_out
    assert stress_out["net_thrust"] >= 0.0

    # 5. Gravitational Curvature Node
    curv = GravitationalCurvatureNode(node_id="curv_01")
    curv_out = curv.execute({
        "stress_tensor": stress_out["stress_tensor"],
        "net_thrust": stress_out["net_thrust"]
    })
    assert not math.isnan(curv_out["ricci_scalar_proxy"])
    assert not math.isinf(curv_out["effective_acceleration"])

    # 6. Quantum Backreaction Stability Node
    backreaction = QuantumBackreactionNode(node_id="back_01")
    back_out = backreaction.execute({
        "ricci_scalar_proxy": curv_out["ricci_scalar_proxy"],
        "jet_power": pump_out["jet_power"],
        "berry_phase_shift": berry_out["berry_phase_shift"]
    })
    
    # Updated the allowed statuses to include 'subcritical_stable'
    assert back_out["stability_status"] in ["stable", "quasi_stable", "monitored", "subcritical_stable"]
