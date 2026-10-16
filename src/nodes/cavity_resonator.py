"""
Photonic Crystal Nanobeam Cavity Resonator Node with Lindblad Dissipation.
Scaffold phase 2.1: Implements non-equilibrium Lindblad dynamics for open
cavity modes, backward-compatible with legacy bare/screened phase contracts.

Governing equation:
    d rho / dt = -i [H_eff, rho] + sum_k ( L_k rho L_k^dagger - 1/2 {L_k^dagger L_k, rho} )

References:
    - docs/07_Lindblad_Dynamics_and_Cavity_Entanglement_Transfer.md
    - El Anouz, El Allati, Saif (2020) non-Markovian open systems.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
import numpy as np

from .base import Node


def _annihilation_operator(dim: int) -> np.ndarray:
    a = np.zeros((dim, dim), dtype=complex)
    for n in range(1, dim):
        a[n - 1, n] = np.sqrt(n)
    return a


def _build_liouvillian(h_eff: np.ndarray, c_ops: List[tuple[np.ndarray, float]], dim: int) -> np.ndarray:
    dim2 = dim * dim
    eye = np.eye(dim, dtype=complex)

    unitary_super = -1j * (np.kron(h_eff, eye) - np.kron(eye, h_eff.T))

    dissipator_super = np.zeros((dim2, dim2), dtype=complex)
    for c, rate in c_ops:
        if rate <= 0.0:
            continue
        c_dag_c = c.conj().T @ c
        term1 = np.kron(c, c.conj())
        term2 = 0.5 * np.kron(c_dag_c, eye)
        term3 = 0.5 * np.kron(eye, c_dag_c.T)
        dissipator_super += rate * (term1 - term2 - term3)

    return unitary_super + dissipator_super


class CavityResonatorNode(Node):
    """
    Simulates optical/microwave cavity subject to intrinsic dissipation
    and thermal bath coupling. Preserves legacy screened_phase / leakage
    contract while computing quantum master equation evolution.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        node_id: Optional[str] = None,
        **config: Any
    ):
        chosen_id = node_id or name or "cavity_resonator"
        super().__init__(node_id=chosen_id, name=chosen_id, **config)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        bare_phase: float = float(inputs.get("bare_phase", 1.0))
        leakage_ratio: float = float(inputs.get("leakage_ratio", self.config.get("leakage_ratio", 0.05)))
        angular_deficit_deg: float = float(inputs.get("angular_deficit_deg", 0.0))
        phase_freq: float = float(inputs.get("phase_frequency", 0.05))

        cavity_q: float = float(inputs.get("cavity_q", self.config.get("cavity_q", 1e5)))
        damping_factor: float = float(inputs.get("damping_factor", self.config.get("damping_factor", 1.0)))
        n_th: float = float(inputs.get("n_thermal", inputs.get("n_th", self.config.get("n_thermal", 0.0))))
        omega_r: float = float(inputs.get("omega_r", inputs.get("resonance_frequency", 1.0)))
        fock_dim: int = int(inputs.get("fock_dim", self.config.get("fock_dim", 4)))
        dt: float = float(inputs.get("dt", 0.1))
        n_steps: int = int(inputs.get("n_steps", 20))
        initial_state_kind: str = str(inputs.get("initial_state", self.config.get("initial_state", "vacuum")))

        kappa = (omega_r / max(cavity_q, 1.0)) * damping_factor

        rho_0 = np.zeros((fock_dim, fock_dim), dtype=complex)
        if initial_state_kind == "single_photon" and fock_dim > 1:
            rho_0[1, 1] = 1.0 + 0.0j
        else:
            rho_0[0, 0] = 1.0 + 0.0j

        a = _annihilation_operator(fock_dim)
        a_dag = a.conj().T
        h_eff = omega_r * (a_dag @ a)

        c_ops: List[tuple[np.ndarray, float]] = [
            (a, kappa * (n_th + 1.0)),
            (a_dag, kappa * n_th)
        ]

        liouvillian = _build_liouvillian(h_eff, c_ops, fock_dim)
        generator_dt = liouvillian * dt
        evals, evecs = np.linalg.eig(generator_dt)
        exp_evals = np.exp(evals)
        inv_evecs = np.linalg.pinv(evecs)
        prop_matrix = evecs @ np.diag(exp_evals) @ inv_evecs

        rho_t = rho_0.copy()
        n_op = a_dag @ a
        photon_trace: List[float] = []
        max_trace_dev = 0.0

        for _ in range(n_steps):
            rho_vec = rho_t.ravel()
            rho_next_vec = prop_matrix @ rho_vec
            rho_t = rho_next_vec.reshape((fock_dim, fock_dim))
            rho_t = 0.5 * (rho_t + rho_t.conj().T)
            tr = float(np.real(np.trace(rho_t)))
            dev = abs(tr - 1.0)
            if dev > max_trace_dev:
                max_trace_dev = dev
            if tr > 1e-15:
                rho_t = rho_t / tr

            exp_n = float(np.real(np.trace(rho_t @ n_op)))
            photon_trace.append(exp_n)

        final_trace = float(np.real(np.trace(rho_t)))
        final_exp_n = photon_trace[-1] if photon_trace else float(np.real(np.trace(rho_0 @ n_op)))

        fidelity = float(np.real(np.trace(rho_0 @ rho_t)))
        fidelity = max(0.0, min(1.0, fidelity))

        screened_phase = bare_phase * (1.0 - leakage_ratio)
        angular_deficit_rad = math.radians(angular_deficit_deg)

        return {
            "screened_phase": screened_phase,
            "leakage_ratio": leakage_ratio,
            "phase_frequency": phase_freq,
            "angular_deficit_rad": angular_deficit_rad,
            "calibration_status": "scaffold_only",
            "kappa": kappa,
            "final_photon_number": final_exp_n,
            "photon_number_trace": photon_trace,
            "final_trace": final_trace,
            "max_trace_deviation": max_trace_dev,
            "state_fidelity": fidelity,
            "coherence_retention": fidelity
        }
