"""
Visualization Script: Popcorn Vacuum Nucleation & Hubble Tension Compensation.
Generates publication-quality 300 DPI plots demonstrating local quantum bubble
density compensation and its connection to the Hubble tension gap (H0).
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from src.nodes.popcorn_vacuum_density import PopcornVacuumDensityNode, PopcornVacuumConfig


def main():
    print("[*] Running Popcorn Vacuum & Hubble Tension Visualization...")
    
    # 1. Initialize Node & Configuration
    config = PopcornVacuumConfig(
        H0_early=67.4,
        H0_late=73.0,
        bubble_coherence_scale_kpc=12.0
    )
    node = PopcornVacuumDensityNode(config)
    
    # 2. Generate radial distance and synthetic baryonic acceleration profile (NGC 6503 representative)
    r_kpc = np.linspace(0.1, 50.0, 300)
    # Baryonic acceleration falling off with radius (m/s^2)
    g_baryon = 1e-10 * (1.0 / (1.0 + (r_kpc / 3.0)**2))
    
    # 3. Compute Popcorn Vacuum Density & Total Acceleration
    res = node.compute(r_kpc, g_baryon)
    
    # 4. Create Publication-Quality Figure (300 DPI)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Subplot A: Acceleration Profiles (Baryon vs Popcorn vs Total)
    ax1.plot(res["r_kpc"], res["g_baryon"] * 1e12, label=r'Baryonic $g_{\rm bar}$', color='#1f77b4', lw=2.5)
    ax1.plot(res["r_kpc"], res["g_popcorn"] * 1e12, label=r'Popcorn Vacuum $g_{\rm pop}$', color='#ff7f0e', lw=2.5, linestyle='--')
    ax1.plot(res["r_kpc"], res["g_total"] * 1e12, label=r'Total Effective $g_{\rm tot}$', color='#2ca02c', lw=3)
    
    ax1.set_title('SDF-QPUMP: Popcorn Vacuum Density Compensation', fontsize=12, fontweight='bold', pad=12)
    ax1.set_xlabel('Galactic Radius $r$ (kpc)', fontsize=11)
    ax1.set_ylabel('Acceleration ($10^{-12}\\text{ m/s}^2$)', fontsize=11)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=10)
    
    # Subplot B: Hubble Tension Connection & Vacuum Pressure Gap
    # Illustrating early vs late H0 energy density discrepancy compensation
    delta_hubble_profile = res["delta_H0"] * (1.0 - np.exp(-res["r_kpc"] / 15.0))
    ax2.plot(res["r_kpc"], delta_hubble_profile, color='#d62728', lw=2.5, label=r'Resolved $\Delta H_0$ Gap (km/s/Mpc)')
    ax2.axhline(res["delta_H0"], color='gray', linestyle=':', label=r'Global Discrepancy ($\Delta H_0 = 5.6$)')
    
    ax2.set_title('Hubble Tension ($\Delta H_0$) Local Vacuum Bridge', fontsize=12, fontweight='bold', pad=12)
    ax2.set_xlabel('Radius / Coherence Coordinate $r$ (kpc)', fontsize=11)
    ax2.set_ylabel('Effective $\Delta H_0$ Contribution', fontsize=11)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=10)
    
    plt.tight_layout()
    
    # 5. Save Output
    os.makedirs("outputs/plots", exist_ok=True)
    out_path = "outputs/plots/popcorn_vacuum_hubble_tension.png"
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"[+] Saved Popcorn Vacuum & Hubble Tension plot to {out_path}")
    plt.close()


if __name__ == "__main__":
    main()
