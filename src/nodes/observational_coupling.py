"""
Observational Coupling Node (Branch Extension)
Connects radial coherent noise flux (J_r) and isotropic background noise
to effective gravitational coupling G_eff and empirical observational windows:
1. Low-acceleration regime (MOND/SPARC Galactic Rotation Curves)
2. Sub-millimeter laboratory tests (Eot-Wash Yukawa limit)
"""

from typing import Dict, Any, Optional
import math
from src.nodes.base import Node


class ObservationalCouplingNode(Node):
    """
    Branch node mapping radial flux J_r and omnidirectional background noise
    to effective gravitational scale G_eff(r) and observational observables.
    """

    def __init__(
        self,
        node_id: str = "observational_coupling",
        g_0: float = 6.67430e-11,
        eta_coupling: float = 0.05,
        a0_mond: float = 1.2e-10,
        default_sigma_omni: float = 1.0,
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(node_id=node_id, label=label, config=config)
        self.g_0 = float(g_0)
        self.eta_coupling = float(eta_coupling)
        self.a0_mond = float(a0_mond)
        self.default_sigma_omni = float(default_sigma_omni)

    def compute_effective_g(
        self,
        radial_flux_jr: float,
        sigma_omni: float,
        radius: float,
    ) -> float:
        """
        G_eff(r) = G_0 * [1 + eta * (J_r / (sigma_omni^2 + epsilon))]
        """
        epsilon = 1e-12
        flux_ratio = radial_flux_jr / (sigma_omni ** 2 + epsilon)
        g_eff = self.g_0 * (1.0 + self.eta_coupling * flux_ratio)
        return float(g_eff)

    def compute_mond_acceleration(
        self,
        baryonic_acc: float,
        g_eff_ratio: float,
    ) -> Dict[str, float]:
        """
        Evaluates the transition to low-acceleration MOND regime:
        g_obs = sqrt(g_bar * a0) when g_bar << a0
        """
        g_bar_eff = baryonic_acc * g_eff_ratio
        if g_bar_eff <= 0.0:
            return {"g_baryonic_effective": 0.0, "g_observed": 0.0, "mond_boost_factor": 1.0}

        if g_bar_eff < self.a0_mond:
            g_obs = math.sqrt(g_bar_eff * self.a0_mond)
        else:
            g_obs = g_bar_eff

        boost = g_obs / (g_bar_eff + 1e-18)
        return {
            "g_baryonic_effective": float(g_bar_eff),
            "g_observed": float(g_obs),
            "mond_boost_factor": float(boost),
        }

    def compute_eotwash_yukawa_bound(
        self,
        radius_micron: float,
        g_eff_ratio: float,
    ) -> Dict[str, Any]:
        """
        Compares with sub-millimeter Eot-Wash bounds:
        V(r) = -G/r * (1 + alpha * exp(-r / lambda))
        """
        alpha_eff = g_eff_ratio - 1.0
        is_consistent_with_lab = abs(alpha_eff) < 0.2
        return {
            "radius_micron": float(radius_micron),
            "effective_alpha_yukawa": float(alpha_eff),
            "consistent_with_lab_limits": bool(is_consistent_with_lab),
        }

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        payload = inputs if inputs is not None else {}

        # 1. Extract inputs safely
        jr = float(payload.get("radial_flux_jr", payload.get("total_radial_flux", 0.0)))
        radius = float(payload.get("mean_radius", payload.get("radius", 1.0)))
        sigma_omni = float(payload.get("sigma_omni", self.default_sigma_omni))
        baryonic_acc = float(payload.get("baryonic_acc", 1e-11))

        # 2. Compute effective coupling
        g_eff = self.compute_effective_g(radial_flux_jr=jr, sigma_omni=sigma_omni, radius=radius)
        g_eff_ratio = g_eff / self.g_0

        # 3. Observational mappings
        mond_res = self.compute_mond_acceleration(baryonic_acc, g_eff_ratio)
        eotwash_res = self.compute_eotwash_yukawa_bound(
            radius_micron=radius * 1e6 if radius < 1e-3 else 50.0,
            g_eff_ratio=g_eff_ratio,
        )

        return {
            "status": "success",
            "node_id": self.node_id,
            "inputs": {
                "radial_flux_jr": jr,
                "sigma_omni": sigma_omni,
                "radius": radius,
            },
            "effective_gravity": {
                "g_0": self.g_0,
                "g_eff": g_eff,
                "g_eff_ratio": g_eff_ratio,
            },
            "mond_sparc_observational": mond_res,
            "eotwash_laboratory_observational": eotwash_res,
        }
