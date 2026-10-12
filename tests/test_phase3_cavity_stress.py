"""Phase 3 tests: Cavity Resonator, Boundary Stress Integrator, and multi-cycle coupling."""

import pytest
import math
from src.core import Graph
from src.nodes.peristaltic_pump import PeristalticPumpNode
from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode


class TestPhase3CavityStressPipeline:
    """Verifies node computations, end-to-end DAG execution, and multi-cycle stability."""

    def test_cavity_resonator_node_direct(self):
        node = CavityResonatorNode("cavity_1")
        res = node.compute({
            "bare_phase": 3.14159,
            "angular_deficit_deg": 180.0,
            "leakage_ratio": 0.1,
        })

        assert math.isclose(res["screened_phase"], 3.14159 * 0.9, rel_tol=1e-5)
        assert math.isclose(res["angular_deficit_rad"], math.pi, rel_tol=1e-5)
        assert res["calibration_status"] == "scaffold_only"
        assert res["leakage_ratio"] == 0.1

    def test_boundary_stress_integrator_node_direct(self):
        node = BoundaryStressIntegratorNode("stress_1")

        # Test Newtonian regime (high jet power)
        res_high = node.compute({"jet_power": 10.0, "noise_floor": 1e-4})
        assert res_high["regime"] == "newtonian"
        assert res_high["snr"] == pytest.approx(10.0 / 1e-4)
        assert res_high["net_thrust"] > 9.99
        assert len(res_high["stress_tensor"]) == 4

        # Test sub-noise regime (low jet power)
        res_low = node.compute({"jet_power": 1e-5, "noise_floor": 1e-3})
        assert res_low["regime"] == "sub-noise"
        assert res_low["net_thrust"] == 0.0

    def test_phase3_full_dag_execution(self):
        """Constructs and runs the full Cavity -> Berry -> Pump -> Stress DAG."""
        g = Graph()

        # Add node instances (add_node takes 1 argument: the node instance)
        g.add_node(CavityResonatorNode("cavity"))
        g.add_node(BerryTorqueBridgeNode("berry"))
        g.add_node(PeristalticPumpNode("pump"))
        g.add_node(BoundaryStressIntegratorNode("stress"))

        # Connect ports according to physical flow
        g.connect("cavity", "screened_phase", "berry", "screened_phase")
        g.connect("cavity", "angular_deficit_rad", "berry", "angular_deficit_rad")
        g.connect("cavity", "phase_frequency", "pump", "phase_frequency")
        g.connect("berry", "berry_phase_shift", "pump", "berry_phase_shift")
        g.connect("pump", "jet_power", "stress", "jet_power")

        # Initial seed inputs for root and intermediate requirements
        initial_inputs = {
            "cavity": {
                "bare_phase": 2.5,
                "angular_deficit_deg": 45.0,
                "leakage_ratio": 0.05,
            },
            "berry": {
                "alpha_target": 1.2,
            },
            "pump": {
                "drive_amplitude": 1.5,
            },
            "stress": {
                "noise_floor": 1e-4,
            },
        }

        results = g.run(initial_inputs)

        # Verify all nodes executed successfully
        assert "cavity" in results
        assert "berry" in results
        assert "pump" in results
        assert "stress" in results

        # Verify stress coupling
        assert results["stress"]["net_thrust"] > 0.0
        assert results["stress"]["regime"] == "newtonian"

        # Verify Berry torque coupling
        assert "torque_correction" in results["berry"]
        assert "berry_phase_shift" in results["berry"]

    def test_multi_cycle_pumping_dynamics(self):
        """Validates pump stability and cumulative behavior over multiple operational cycles."""
        pump = PeristalticPumpNode("pump_cycle")
        stress = BoundaryStressIntegratorNode("stress_cycle")

        accumulated_thrust = 0.0
        cycles = 10

        for cycle in range(1, cycles + 1):
            drive = 1.0 + 0.1 * math.sin(cycle * math.pi / 5.0)
            p_out = pump.compute({
                "drive_amplitude": drive,
                "berry_phase_shift": 1.05,
                "phase_frequency": 50.0,
            })

            s_out = stress.compute({
                "jet_power": p_out["jet_power"],
                "noise_floor": 1e-4,
            })

            assert s_out["net_thrust"] > 0.0
            accumulated_thrust += s_out["net_thrust"]

        assert accumulated_thrust > 0.0
        assert math.isfinite(accumulated_thrust)
