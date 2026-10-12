"""
qpump.engine

Time-stepped and stateful dynamical execution engine for QPUMP Dags.
"""
from typing import Any, Callable, Dict, List, Optional
from .quantum_geometry import QuantumGeometryEngine
from .core import Graph


class TimeSteppedPipelineRunner:
    """
    Runs a QPUMP Graph over discrete time steps (simulating multiple pump cycles)
    while providing stateful feedback and recording time-series observables.
    """

    def __init__(
        self,
        graph: Graph,
        dt: float = 0.01,
        feedback_callback: Optional[Callable[[Dict[str, Dict[str, Any]], float], Dict[str, Dict[str, Any]]]] = None,
    ) -> None:
        self.graph = graph
        self.dt = dt
        self.feedback_callback = feedback_callback
        self.history: List[Dict[str, Any]] = []

    def run_steps(
        self,
        n_steps: int,
        initial_state: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Runs n_steps successively, passing feedback between steps.
        """
        current_state = {k: dict(v) for k, v in (initial_state or {}).items()}
        self.history.clear()

        for step_idx in range(n_steps):
            t = step_idx * self.dt
            step_outputs = self.graph.run(current_state)
            
            snapshot = {
                "step": step_idx,
                "time": t,
                "values": step_outputs,
            }
            self.history.append(snapshot)

            # Apply feedback for next step if provided
            if self.feedback_callback:
                current_state = self.feedback_callback(step_outputs, t)
            else:
                # Default: carry forward outputs as next state inputs
                current_state = {k: dict(v) for k, v in step_outputs.items()}

        return self.history
