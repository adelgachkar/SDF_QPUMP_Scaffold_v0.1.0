import numpy as np
import pytest

from src.nodes.optical_phase_step import OpticalPhaseStepNode


def test_optical_phase_step_single_packet():
    node = OpticalPhaseStepNode(
        node_id="opt_test",
        k0=2.0,
        n_eff_base=1.5,
        dz_step=0.1,
        omega=1.0,
        dt_step=0.05,
    )
    # delta_phi = (2.0 * 1.5 * 0.1) + (1.0 * 0.05) = 0.3 + 0.05 = 0.35 rad
    expected_dphi = 0.35
    assert np.isclose(node.compute_phase_step(), expected_dphi)

    pkt = {"phase": 0.1, "amplitude": 2.0, "time": 0.5, "z": 1.2}
    res = node.execute({"packet": pkt})

    assert res["packet_count"] == 1
    out_pkt = res["stepped_packets"][0]
    assert np.isclose(out_pkt["phase"], 0.45)
    assert np.isclose(out_pkt["amplitude"], 2.0)
    assert out_pkt["optical_stepped"] is True
    assert res["status"] == "ready_for_radial_propagation"


def test_optical_phase_step_queue_pipeline():
    node = OpticalPhaseStepNode(node_id="opt_queue")
    queue_input = [
        {"phase": 0.0, "amplitude": 1.0},
        {"phase": np.pi, "amplitude": 0.5},
    ]

    res = node.execute({"queue": queue_input, "permittivity_mod": 0.2})
    assert res["packet_count"] == 2
    assert len(res["stepped_packets"]) == 2
    assert "delta_phi_applied" in res
    assert res["stepped_packets"][0]["phase"] > 0.0
