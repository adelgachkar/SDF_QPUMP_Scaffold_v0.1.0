"""
Resonant Spinon Zero Mode Node (Chen & Lado, Phys. Rev. Research 2, 033466 (2020)).

Models the resonant spinon zero-mode induced by magnetic impurities (vacancies)
in a Dirac Quantum Spin Liquid (pi-flux state) and computes:
  1. The resonant local density of states (LDOS) peak around zero energy.
  2. The local two-spinon dynamical structure factor S(r, omega).
  3. The zero-mode quenching / interference factor as a function of impurity density.
Integrates with QPUMP Cavity & Popcorn vacuum nodes.
"""

from typing import Any, Dict, List
import numpy as np

try:
    from .base import Node
except ImportError:  # pragma: no cover - fallback for direct execution
    from src.nodes.base import Node


class ResonantSpinonZeroModeNode(Node):
    """
    Computes resonant zero-mode spectral signatures induced by S=1/2 impurities
    in Dirac spin liquids, translating vacancy-induced resonances to vacuum cavity
    wall excitation proxies.
    """

    def __init__(
        self,
        node_id: str = "resonant_spinon_zero_mode_1",
        label: str = "Resonant Spinon Zero Mode Node",
        config: Dict[str, Any] = None,
        name: str = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(node_id=node_id, label=label, config=config, name=name, **kwargs)
        self.config.setdefault("hopping_t", 1.0)
        self.config.setdefault("default_eta", 0.05)
        self.config.setdefault("nu_critical", 0.15)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        t = float(self.config.get("hopping_t", 1.0))
        eta = float(inputs.get("eta", self.config.get("default_eta", 0.05)))
        nu = float(inputs.get("impurity_density", 0.02))
        T = float(inputs.get("temperature", 0.01))
        d_bonds = int(inputs.get("distance_bonds", 1))
        cavity_coupling = float(inputs.get("cavity_coupling", 1.0))

        # 1. Zero-mode interference / quenching (Eq. 10 of the paper)
        nu_crit = float(self.config.get("nu_critical", 0.15))
        persistence = float(1.0 / (1.0 + (nu / nu_crit) ** 2))

        # 2. Distance dependence: odd-bond neighbors carry zero-mode weight
        sublattice_parity_weight = 1.0 if (d_bonds % 2 != 0) else 0.15
        spatial_decay = float(np.exp(-(d_bonds - 1) / 3.0))
        site_weight = sublattice_parity_weight * spatial_decay

        # 3. Frequency grid
        raw_omega = inputs.get("omega_range", None)
        if raw_omega is None:
            omega_arr = np.linspace(-0.5 * t, 0.5 * t, 41)
        else:
            omega_arr = np.array(raw_omega, dtype=float)

        # 4. Resonant LDOS: Dirac background |w|/(2 pi v_F^2) + Lorentzian zero mode
        v_f = np.sqrt(3) * t / 2.0
        rho_background = np.abs(omega_arr) / (2.0 * np.pi * (v_f**2) + 1e-12)
        gamma_eff = eta * (1.0 + 2.0 * nu)
        lorentzian_peak = (site_weight * persistence / np.pi) * (gamma_eff / (omega_arr**2 + gamma_eff**2))
        ldos = rho_background + lorentzian_peak
        resonant_ldos_zero = float(site_weight * persistence / (np.pi * gamma_eff))

        # 5. Local dynamical spin structure factor S(r, omega) (Eq. 12 approximation)
        def fermi(e):
            return 1.0 / (np.exp(np.clip(e / max(T, 1e-6), -50, 50)) + 1.0)

        f_vals = fermi(omega_arr)
        dw = (omega_arr[-1] - omega_arr[0]) / max(len(omega_arr) - 1, 1)
        s_vals = np.zeros_like(omega_arr)
        for i, w in enumerate(omega_arr):
            shift_idx = int(np.round(w / dw)) if dw > 0 else 0
            overlap = float(np.sum(ldos * np.roll(ldos, shift_idx) * np.abs(f_vals - np.roll(f_vals, shift_idx))) * dw)
            s_vals[i] = overlap + (site_weight * persistence * gamma_eff / (w**2 + gamma_eff**2))

        zero_bias_intensity = float(s_vals[len(s_vals) // 2])

        # 6. Effective vacuum energy injection (cavity coupling proxy)
        effective_injection = float(zero_bias_intensity * cavity_coupling * (1.0 + nu))

        return {
            "resonant_ldos_zero": resonant_ldos_zero,
            "zero_bias_intensity": zero_bias_intensity,
            "omega_grid": omega_arr.tolist(),
            "spectral_density": s_vals.tolist(),
            "zero_mode_persistence": persistence,
            "effective_vacuum_injection": effective_injection,
        }
