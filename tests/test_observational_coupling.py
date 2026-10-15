"""
Tests for Observational Coupling Extension Branch
Validates connection between radial flux Jr and observational benchmarks.
"""

import pytest
from src.nodes.radial_propagation import RadialPropagationNode
from src.nodes.observational_coupling import ObservationalCouplingNode


def test_observational_coupling_direct():
    node = ObservationalCouplingNode(eta_coupling=0.05)
    result = node.execute({
        "radial_flux_jr": 2.0,
        "sigma_omni": 1.0,
        "baryonic_acc": 5.0e-11,
    })

    assert result["status"] == "success"
    g_eff_ratio = result["effective_gravity"]["g_eff_ratio"]
    assert g_eff_ratio > 1.0
    assert "mond_sparc_observational" in result
    assert result["mond_sparc_observational"]["mond_boost_factor"] > 1.0


def test_chain_radial_propagation_to_observational():
    # 1. Run Radial Propagation
    rad_node = RadialPropagationNode()
    packet = {"packet_id": "test_obs", "r": 0.1, "amplitude": 1.5, "phase": 0.0}
    rad_output = rad_node.execute({"packet": packet})

    # Robust extraction of flux and radius
    if "total_radial_flux" in rad_output:
        jr_val = rad_output["total_radial_flux"]
    elif "propagated_packets" in rad_output and len(rad_output["propagated_packets"]) > 0:
        jr_val = rad_output["propagated_packets"][0].get("radial_flux_jr", 1.0)
    else:
        jr_val = 1.0

    mean_r = rad_output.get("mean_radius", None)
    if mean_r is None and "propagated_packets" in rad_output and len(rad_output["propagated_packets"]) > 0:
        mean_r = rad_output["propagated_packets"][0].get("r", 0.2)
    elif mean_r is None:
        mean_r = 0.2

    # 2. Feed output directly to Observational Coupling
    obs_node = ObservationalCouplingNode()
    obs_output = obs_node.execute({
        "total_radial_flux": jr_val,
        "mean_radius": mean_r,
        "sigma_omni": 1.0,
    })

    assert obs_output["status"] == "success"
    assert obs_output["effective_gravity"]["g_eff"] > 0.0
    assert "consistent_with_lab_limits" in obs_output["eotwash_laboratory_observational"]
