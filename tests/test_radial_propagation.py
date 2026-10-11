import numpy as np
import pytest

from qpump.nodes.radial_propagation import RadialPropagationNode


def test_radial_propagation_single_packet():
    node = RadialPropagationNode(
        node_id="rad_test",
        delta_r=0.2,
        k_radial=2.0,
        alpha_div=0.5,
        gamma_loss=0.0,
        r_min=0.1,
    )

    pkt = {"amplitude": 1.0, "phase": 0.0, "r": 1.0}
    res = node.execute({"packet": pkt})

    assert res["packet_count"] == 1
    out_pkt = res["propagated_packets"][0]

    # r_new = 1.0 + 0.2 = 1.2
    assert np.isclose(out_pkt["r"], 1.2)
    # amp_new = 1.0 * (1.0 / 1.2)^0.5
    expected_amp = (1.0 / 1.2) ** 0.5
    assert np.isclose(out_pkt["amplitude"], expected_amp)
    # phase_new = 0.0 + (2.0 * 0.2) = 0.4 rad
    assert np.isclose(out_pkt["phase"], 0.4)
    assert out_pkt["radial_propagated"] is True
    assert res["status"] == "radial_propagation_complete"


def test_radial_propagation_chain_from_optical_step():
    from qpump.nodes.optical_phase_step import OpticalPhaseStepNode

    opt_node = OpticalPhaseStepNode(node_id="opt")
    rad_node = RadialPropagationNode(node_id="rad")

    input_queue = [
        {"amplitude": 1.0, "phase": 0.0, "r": 0.5},
        {"amplitude": 0.8, "phase": np.pi / 2, "r": 1.0},
    ]

    opt_out = opt_node.execute({"queue": input_queue})
    rad_out = rad_node.execute(opt_out)

    assert rad_out["packet_count"] == 2
    assert len(rad_out["propagated_packets"]) == 2
    assert rad_out["total_radial_flux"] > 0.0
    for p in rad_out["propagated_packets"]:
        assert p["optical_stepped"] is True
        assert p["radial_propagated"] is True
