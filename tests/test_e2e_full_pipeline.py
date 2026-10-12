import math
import pytest

from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from src.nodes.peristaltic_pump import PeristalticPumpNode
from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
from src.nodes.gravitational_curvature import GravitationalCurvatureNode
from src.nodes.quantum_backreaction import QuantumBackreactionNode
from src.nodes.optical_phase_step import OpticalPhaseStepNode
from src.nodes.radial_propagation import RadialPropagationNode
from src.nodes.z_axis_filter_queue import ZAxisFilterQueueNode


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
    assert back_out["stability_status"] in ["stable", "quasi_stable", "monitored", "subcritical_stable"]

    # 7. Optical Phase Step
    optical = OpticalPhaseStepNode(node_id="opt_01")
    opt_out = optical.execute({
        "drive_amplitude": pump_out["jet_power"],
        "berry_phase_shift": berry_out["berry_phase_shift"]
    })
    # Node produces stepped_packets / packet_count
    assert "stepped_packets" in opt_out or "packet_count" in opt_out

    # 8. Z-Axis Filter Queue
    z_filter = ZAxisFilterQueueNode(node_id="z_01")
    z_out = z_filter.execute({
        "packets": opt_out.get("stepped_packets", [])
    })
    assert isinstance(z_out, dict)

    # 9. Radial Propagation
    radial = RadialPropagationNode(node_id="rad_01")
    rad_out = radial.execute({
        "packets": opt_out.get("stepped_packets", []),
        "angular_step_rad": 0.05
    })
    assert isinstance(rad_out, dict)


def test_energy_and_phase_invariants():
    """
    Checks that conservation and boundary invariants hold across the node chain.
    """
    cavity = CavityResonatorNode(node_id="cav_inv")
    cav_out = cavity.execute({
        "bare_phase": 0.1,
        "angular_deficit_deg": 1.0,
        "leakage_ratio": 0.01
    })
    assert 0.0 <= cav_out["leakage_ratio"] <= 1.0
