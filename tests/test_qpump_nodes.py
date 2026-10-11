"""Tests for the Q-PUMP scaffold nodes pipeline."""

from qpump.nodes.cavity_resonator import CavityResonatorNode
from qpump.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from qpump.nodes.peristaltic_pump import PeristalticPumpNode
from qpump.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode


def test_qpump_pipeline_flow():
    # 1. مقداردهی نود کاواک
    cavity = CavityResonatorNode(node_id="cavity_01")
    cavity_out = cavity.execute({
        "bare_phase": 146.82,
        "angular_deficit_deg": 7.35614,
        "leakage_ratio": 1.0 / 15.0
    })
    assert "screened_phase" in cavity_out
    assert cavity_out["calibration_status"] == "scaffold_only"

    # 2. نود پل گشتاور و فاز بری
    berry = BerryTorqueBridgeNode(node_id="berry_01")
    berry_out = berry.execute({
        "screened_phase": cavity_out["screened_phase"],
        "alpha_target": 137.035999,
        "angular_deficit_rad": cavity_out["angular_deficit_rad"]
    })
    assert "berry_phase_shift" in berry_out
    assert "torque_correction" in berry_out

    # 3. نود پمپ پریستالتیک فاز
    pump = PeristalticPumpNode(node_id="pump_01")
    pump_out = pump.execute({
        "drive_amplitude": 1.0,
        "berry_phase_shift": berry_out["berry_phase_shift"],
        "phase_frequency": cavity_out["phase_frequency"]
    })
    assert pump_out["jet_power"] > 0
    assert len(pump_out["phase_flux_vector"]) == 3

    # 4. نود ادغام تنش مرزی
    stress = BoundaryStressIntegratorNode(node_id="stress_01")
    stress_out = stress.execute({
        "jet_power": pump_out["jet_power"],
        "noise_floor": 1e-4
    })
    assert stress_out["regime"] == "newtonian"
    assert len(stress_out["stress_tensor"]) == 4

    print("\n[SUCCESS] Pipeline passed: All 4 nodes executed and linked successfully!")


if __name__ == "__main__":
    test_qpump_pipeline_flow()
