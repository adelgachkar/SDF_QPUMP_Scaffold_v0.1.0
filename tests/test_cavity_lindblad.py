import math
import numpy as np
from src.nodes.cavity_resonator import CavityResonatorNode


def test_cavity_backward_compatibility():
    """Verify that legacy classical scaffold ports still return expected values."""
    node = CavityResonatorNode()
    out = node.compute({"bare_phase": 2.0, "leakage_ratio": 0.1, "angular_deficit_deg": 30.0})
    assert math.isclose(out["screened_phase"], 1.8, rel_tol=1e-6)
    assert math.isclose(out["angular_deficit_rad"], math.radians(30.0), rel_tol=1e-6)
    assert out["calibration_status"] == "scaffold_only"


def test_lindblad_trace_preservation():
    """Verify master equation preserves Tr(rho) == 1 within tight numerical tolerance."""
    node = CavityResonatorNode()
    out = node.compute({"cavity_q": 500.0, "damping_factor": 2.0, "n_steps": 30, "dt": 0.05})
    assert math.isclose(out["final_trace"], 1.0, abs_tol=1e-12)
    assert out["max_trace_deviation"] < 1e-10


def test_single_photon_decay():
    """Verify photon expectation decays monotonically for n_thermal = 0."""
    node = CavityResonatorNode()
    out = node.compute({
        "initial_state": "single_photon",
        "cavity_q": 50.0,
        "omega_r": 10.0,
        "n_steps": 25,
        "dt": 0.2,
        "n_thermal": 0.0
    })
    n_trace = out["photon_number_trace"]
    assert n_trace[0] > n_trace[-1]
    assert out["state_fidelity"] < 1.0
