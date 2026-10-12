import math
import pytest
from src.quantum_geometry import QuantumGeometryEngine
from src.core import Graph
from src.nodes.base import PassthroughNode
from src.engine import TimeSteppedPipelineRunner


def test_berry_curvature_monopole_symmetry():
    # Berry curvature at north pole (z > 0) must be negative (for spin 1/2)
    f_z, gtrace = QuantumGeometryEngine.two_level_berry_curvature(0.0, 0.0, 1.0)
    assert f_z == -0.5
    assert gtrace == 0.5


def test_adiabatic_pump_cycle_phase():
    res = QuantumGeometryEngine.adiabatic_pump_cycle(amplitude=1.0, detuning=1.0, cycles_n=1.0)
    assert "berry_phase_rad" in res
    assert "geometric_torque" in res
    # Phase should be finite and bounded
    assert abs(res["berry_phase_rad"]) > 0.0


def test_time_stepped_runner():
    g = Graph()
    node = PassthroughNode("dyn_node")
    g.add_node(node)
    runner = TimeSteppedPipelineRunner(graph=g, dt=0.1)

    # Simple dynamic accumulation
    def feedback(step_outputs, t):
        curr = step_outputs["dyn_node"].get("accumulated", 0.0)
        return {"dyn_node": {"accumulated": curr + 1.0, "timestamp": t}}

    runner.feedback_callback = feedback
    history = runner.run_steps(n_steps=5, initial_state={"dyn_node": {"accumulated": 0.0}})

    assert len(history) == 5
    assert history[-1]["values"]["dyn_node"]["accumulated"] == 4.0
