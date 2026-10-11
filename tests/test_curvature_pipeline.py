"""Tests for Curvature and Quantum Backreaction pipeline extensions."""

from qpump.nodes.cavity_resonator import CavityResonatorNode
from qpump.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from qpump.nodes.peristaltic_pump import PeristalticPumpNode
from qpump.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
from qpump.nodes.gravitational_curvature import GravitationalCurvatureNode
from qpump.nodes.quantum_backreaction import QuantumBackreactionNode


def test_full_curvature_backreaction_chain():
    # 1. Cavity
    cavity = CavityResonatorNode(node_id="cav_01")
    c_out = cavity.execute({"bare_phase": 146.82, "angular_deficit_deg": 7.35614})

    # 2. Berry Torque Bridge
    berry = BerryTorqueBridgeNode(node_id="berry_01")
    b_out = berry.execute({
        "screened_phase": c_out["screened_phase"],
        "alpha_target": 137.035999,
        "angular_deficit_rad": c_out["angular_deficit_rad"]
    })

    # 3. Peristaltic Pump
    pump = PeristalticPumpNode(node_id="pump_01")
    p_out = pump.execute({
        "drive_amplitude": 1.0,
        "berry_phase_shift": b_out["berry_phase_shift"],
        "phase_frequency": c_out["phase_frequency"]
    })

    # 4. Boundary Stress Integrator
    stress = BoundaryStressIntegratorNode(node_id="stress_01")
    s_out = stress.execute({
        "jet_power": p_out["jet_power"],
        "noise_floor": 1e-4
    })

    # 5. Gravitational Curvature Node
    curv = GravitationalCurvatureNode(node_id="curv_01")
    curv_out = curv.execute({
        "stress_tensor": s_out["stress_tensor"],
        "net_thrust": s_out["net_thrust"]
    })

    assert "ricci_scalar_proxy" in curv_out
    assert curv_out["effective_acceleration"] >= 0.0
    assert curv_out["curvature_regime"] in ["strong_field_curvature", "perturbative_linear", "asymptotically_flat"]

    # 6. Quantum Backreaction Node
    backreaction = QuantumBackreactionNode(node_id="back_01")
    br_out = backreaction.execute({
        "ricci_scalar_proxy": curv_out["ricci_scalar_proxy"],
        "jet_power": p_out["jet_power"],
        "berry_phase_shift": b_out["berry_phase_shift"]
    })

    assert 0.0 <= br_out["damping_factor"] <= 1.0
    assert br_out["conservation_divergence"] >= 0.0
    assert br_out["stability_status"] in ["subcritical_stable", "supercritical_turbulent"]

    print("\n[SUCCESS] Extended 6-node Gravity-Dynamics pipeline passed successfully!")
