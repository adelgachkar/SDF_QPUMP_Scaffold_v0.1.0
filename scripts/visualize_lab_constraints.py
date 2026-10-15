"""
visualize_lab_constraints.py
-----------------------------
Generates exclusion plots for fifth-force Yukawa parameter space (alpha, lambda)
comparing Eöt-Wash torsion balances and Cold-Atom interferometers.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join("outputs", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9.5,
    "figure.autolayout": True,
    "grid.alpha": 0.35,
    "grid.linestyle": ":"
})

def plot_yukawa_exclusion():
    print("[*] Generating Fifth-Force / Laboratory Exclusion Bounds...")

    # Range of lambda from 100 nm to 1 cm (in meters)
    lambd = np.logspace(-7, -2, 400)

    # Parametric exclusion curves (approximate Adelberger / Eöt-Wash & Cold Atom bounds)
    # Eöt-Wash constraint curve: sensitivity optimal between 40 um and 1 cm
    alpha_eotwash = 1e-3 * (lambd / 1e-3)**(-2.2)
    alpha_eotwash = np.clip(alpha_eotwash, 1e-3, 1e6)

    # Cold-atom interferometry curve: sensitivity optimal between 1 um and 100 um
    alpha_cold_atom = 1e-1 * (lambd / 1e-5)**(-1.8)
    alpha_cold_atom = np.clip(alpha_cold_atom, 1e-2, 1e7)

    # QPUMP theoretical operating regime (green zone)
    qpump_lambd = np.linspace(1e-6, 5e-5, 100)
    qpump_alpha = 5e-5 * np.ones_like(qpump_lambd)

    fig, ax = plt.subplots(figsize=(8, 5.5))

    # Plot exclusion lines
    ax.loglog(lambd * 1e6, alpha_eotwash, color="#d62728", lw=2, label="Eöt-Wash Torsion Balance (Excluded above)")
    ax.fill_between(lambd * 1e6, alpha_eotwash, 1e6, color="#d62728", alpha=0.15)

    ax.loglog(lambd * 1e6, alpha_cold_atom, color="#ff7f0e", lw=2, linestyle="--", label="Cold-Atom Interferometry (Cs / Rb)")
    ax.fill_between(lambd * 1e6, alpha_cold_atom, 1e7, color="#ff7f0e", alpha=0.10)

    # Plot QPUMP allowed operating regime
    ax.scatter(qpump_lambd * 1e6, qpump_alpha, color="#2ca02c", s=25, label="SDF-QPUMP Allowed Operating Zone", zorder=5)

    ax.set_xlim(0.1, 1e4)
    ax.set_ylim(1e-6, 1e5)
    ax.set_xlabel(r"Interaction / Screening Range $\lambda\ (\mathrm{\mu m})$")
    ax.set_ylabel(r"Yukawa Coupling Strength $|\alpha|$")
    ax.set_title(r"Laboratory Fifth-Force Exclusion Limits $(\alpha \text{ vs } \lambda)$")
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True)

    out_path = os.path.join(OUTPUT_DIR, "laboratory_yukawa_exclusion.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"      Saved -> {out_path}")

if __name__ == "__main__":
    plot_yukawa_exclusion()
