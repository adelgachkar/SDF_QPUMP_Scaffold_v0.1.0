"""
tests/test_phase3_cavity_stress.py
Phase 3 Integration and Verification Suite: Cavity Resonator & Boundary Stress.
Uses the primary 'src' architecture.
"""

from __future__ import annotations

import math
import pytest

from src.core import Graph
from src.nodes.cavity_resonator import CavityResonatorNode
from src.nodes.berry_torque_bridge import BerryTorqueBridgeNode
from src.nodes.peristaltic_pump import PeristalticPumpNode
from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode


class TestPhase3CavityStressPipeline:
    """Full verification suite for Phase 3 nodes and end-to-end integration."""

    def test_cavity_resonator_node_isolated(self):
        """Verify CavityResonatorNode correctly computes screened phase, angular deficit, and leakage."""
        node = CavityResonatorNode(name="cavity_test")
        inputs = {
            "bare_phase": 1.5707963267948966,  # pi / 2
            "leakage_ratio": 0.05,
            "angular_deficit_deg": 18.0,
            "boundary_radius_m": 0.005,
        }
        outputs = node.compute(inputs)

        # Screened phase = bare_phase * (1.0 - leakage_ratio)
        expected_screened = 1.5707963267948966 * (1.0 - 0.05)
        assert math.isclose(outputs["screened_phase"], expected_screened, rel_tol=1e-9)

        # Angular deficit deg -> rad
        expected_rad = 18.0 * (math.pi / 180.0)
        assert math.isclose(outputs["angular_deficit_rad"], expected_rad, rel_tol=1e-9)

        assert outputs["calibration_status"] == "scaffold_only"
        assert math.isclose(outputs["leakage_ratio"], 0.05, rel_tol=1e-9)

    def test_boundary_stress_integrator_regimes(self):
        """Verify BoundaryStressIntegratorNode transitions between Newtonian and sub-noise regimes."""
        integrator = BoundaryStressIntegratorNode(name="stress_test")

        # 1. Newtonian regime (jet_power > noise_floor)
        high_power_inputs = {
            "jet_power": 10.0,
            "effective_metric_trace": 1.0,
            "quantum_backreaction_force": 0.1,
            "noise_floor": 1.0,
        }
        out_high = integrator.compute(high_power_inputs)
        assert out_high["stress_regime"] == "newtonian"
        assert math.isclose(out_high["stress_snr"], 10.0, rel_tol=1e-9)
        assert out_high["net_thrust_n"] > 0.0
        assert len(out_high["boundary_stress_tensor"]) == 4

        # 2. Sub-noise regime (jet_power <= noise_floor)
        low_power_inputs = {
            "jet_power": 0.5,
            "effective_metric_trace": 1.0,
            "quantum_backreaction_force": 0.1,
            "noise_floor": 1.0,
        }
        out_low = integrator.compute(low_power_inputs)
        assert out_low["stress_regime"] == "sub-noise"
        assert math.isclose(out_low["stress_snr"], 0.5, rel_tol=1e-9)
        assert math.isclose(out_low["net_thrust_n"], 0.0, abs_tol=1e-12)

    def test_phase3_full_pipeline_dag(self):
        """Verify execution of full Phase 3 DAG from Cavity through Berry & Pump to Stress Integrator."""
        g = Graph(name="phase3_cavity_stress_pipeline")

        cavity = CavityResonatorNode(name="cavity")
        berry = BerryTorqueBridgeNode(name="berry")
        pump = PeristalticPumpNode(name="pump")
        stress = BoundaryStressIntegratorNode(name="stress")

        g.add_node(cavity)
        g.add_node(berry)
        g.add_node(pump)
        g.add_node(stress)

        # Cavity outputs wire into Berry and Pump
        g.add_edge("cavity", "screened_phase", "berry", "driving_phase")
        g.add_edge("cavity", "screened_phase", "pump", "drive_phase")

        # Berry wires into Pump
        g.add_edge("berry", "torque_correction", "pump", "geometric_phase_shift")

        # Pump wires into Boundary Stress Integrator
        g.add_edge("pump", "jet_power", "stress", "jet_power")

        initial_inputs = {
            "cavity": {
                "bare_phase": 3.141592653589793,
                "leakage_ratio": 0.02,
                "angular_deficit_deg": 12.0,
                "boundary_radius_m": 0.01,
            },
            "berry": {
                "quantum_efficiency": 0.95,
                "geometric_coupling": 1.2,
            },
            "pump": {
                "stroke_length_m": 0.05,
                "fluid_density_kg_m3": 1000.0,
                "cycle_frequency_hz": 50.0,
            },
            "stress": {
                "effective_metric_trace": 1.0,
                "quantum_backreaction_force": 0.05,
                "noise_floor": 0.1,
            },
        }

        results = g.execute(initial_inputs)

        assert "cavity" in results
        assert "berry" in results
        assert "pump" in results
        assert "stress" in results

        stress_out = results["stress"]
        assert stress_out["stress_regime"] == "newtonian"
        assert stress_out["net_thrust_n"] > 0.0

        berry_out = results["berry"]
        assert "torque_correction" in berry_out
        assert "berry_phase_shift" in berry_out

    def test_phase3_multi_cycle_stability(self):
        """Verify dynamic stability and thrust accumulation over 10 pump-stress operating cycles."""
        pump = PeristalticPumpNode(name="pump_cycle")
        stress = BoundaryStressIntegratorNode(name="stress_cycle")

        accumulated_thrust = 0.0
        n_cycles = 10

        for cycle in range(n_cycles):
            phase_drive = (cycle + 1) * 0.3141592653589793
            pump_inputs = {
                "drive_phase": phase_drive,
                "geometric_phase_shift": 0.05 * cycle,
                "stroke_length_m": 0.02,
                "fluid_density_kg_m3": 850.0,
                "cycle_frequency_hz": 20.0,
            }
            pump_out = pump.compute(pump_inputs)

            stress_inputs = {
                "jet_power": pump_out["jet_power"],
                "effective_metric_trace": 1.0,
                "quantum_backreaction_force": 0.01,
                "noise_floor": 0.001,
            }
            stress_out = stress.compute(stress_inputs)

            assert stress_out["net_thrust_n"] > 0.0
            accumulated_thrust += stress_out["net_thrust_n"]

        assert accumulated_thrust > 0.0
        assert not math.isnan(accumulated_thrust)
