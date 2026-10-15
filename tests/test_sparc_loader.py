"""
test_sparc_loader.py
--------------------
Tests SPARC galaxy data ingestion and physical acceleration units.
"""

from src.data.sparc_loader import SPARCLoader


def test_sparc_loader_ngc6503():
    data = SPARCLoader.load_galaxy_data("NGC6503")
    assert data["galaxy"] == "NGC6503"
    assert len(data["radius_kpc"]) == 20
    assert len(data["g_obs_si"]) == 20
    assert len(data["g_bar_si"]) == 20

    # Physical sanity checks: accelerations should be in realistic galactic range (10^-12 to 10^-9 m/s^2)
    assert (data["g_obs_si"] > 1e-12).all()
    assert (data["g_obs_si"] < 1e-8).all()
    assert (data["g_bar_si"] > 1e-13).all()
    assert (data["g_bar_si"] < 1e-8).all()
