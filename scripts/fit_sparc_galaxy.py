"""
fit_sparc_galaxy.py
-------------------
Fits SDF-QPUMP observational coupling against canonical SPARC galaxy rotation curves (NGC 6503).
Generates publication plot comparing Observed Velocity vs Baryonic vs Coupled Prediction.
"""

import sys
import os
from pathlib import Path

# Set root directory first before any src imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import matplotlib.pyplot as plt
from src.data.sparc_loader import SPARCLoader

OUTPUT_DIR = os.path.join(ROOT_DIR, "outputs", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.autolayout": True,
    "grid.alpha": 0.35,
    "grid.linestyle": ":"
})


def fit_galaxy():
    print("[*] Loading SPARC benchmark data for NGC 6503...")
    data = SPARCLoader.load_galaxy_data("NGC6503")
    
    r_kpc = data["radius_kpc"]
    v_obs = data["v_obs_kms"]
    v_bar = data["v_bar_kms"]
    g_bar = data["g_bar_si"]
    
    # Calculate model predictions using observational coupling logic:
    # g_obs_model = g_bar / (1 - exp(-sqrt(g_bar / a0)))
    a0 = 1.2e-10  # Acceleration scale in m/s^2 (Milgrom / empirical scale)
    g_model = g_bar / (1.0 - np.exp(-np.sqrt(g_bar / a0)))
    
    # Convert g_model back to predicted velocity V_model = sqrt(g_model * R)
    r_meters = r_kpc * SPARCLoader.KPC_TO_METERS
    v_model_ms = np.sqrt(g_model * r_meters)
    v_model_kms = v_model_ms / 1000.0

    print("[*] Generating SPARC Rotation Curve Comparison Plot...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Subplot 1: Rotation Curve V(R)
    ax1.errorbar(r_kpc, v_obs, yerr=4.0, fmt='o', color="#d62728", label="Observed (SPARC Data)", capsize=3)
    ax1.plot(r_kpc, v_bar, "--", color="gray", lw=1.8, label="Expected Baryonic (Gas + Disk)")
    ax1.plot(r_kpc, v_model_kms, "-", color="#1f77b4", lw=2.2, label=r"SDF-QPUMP Coupling Model ($a_0$)")
    ax1.set_xlabel("Galactocentric Radius $R$ (kpc)")
    ax1.set_ylabel(r"Rotation Velocity $V(R)$ (km/s)")
    ax1.set_title("SPARC Benchmark: Galaxy NGC 6503 Rotation Curve")
    ax1.legend(loc="lower right")
    ax1.grid(True)

    # Subplot 2: Acceleration Relation for NGC 6503
    ax2.loglog(g_bar, data["g_obs_si"], 'o', color="#d62728", alpha=0.85, label="NGC 6503 Data Points")
    ax2.loglog(g_bar, g_bar, "--", color="gray", label=r"Pure Newtonian ($g_{\rm obs} = g_{\rm bar}$)")
    ax2.loglog(g_bar, g_model, "-", color="#1f77b4", lw=2.0, label="Coupled Model Prediction")
    ax2.set_xlabel(r"Baryonic Acceleration $g_{\rm bar}\ (\mathrm{m/s^2})$")
    ax2.set_ylabel(r"Observed Acceleration $g_{\rm obs}\ (\mathrm{m/s^2})$")
    ax2.set_title("Radial Acceleration Dispersion")
    ax2.legend(loc="upper left")
    ax2.grid(True)

    out_path = os.path.join(OUTPUT_DIR, "sparc_ngc6503_fit.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"      Saved -> {out_path}")


if __name__ == "__main__":
    fit_galaxy()
