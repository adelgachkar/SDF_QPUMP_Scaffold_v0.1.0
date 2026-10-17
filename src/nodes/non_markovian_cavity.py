r"""
Non-Markovian Cavity Resonator Node for SDF-QPUMP Framework.
Implements the exact master equation and memory kernel formalism of
Wei-Min Zhang et al. (Phys. Rev. Lett. / exact master equation framework)
for open quantum systems coupled to structured bosonic reservoirs.
"""

from typing import Any, Dict, Optional
import numpy as np

from src.nodes.base import BaseNode


class NonMarkovianCavityNode(BaseNode):
    r"""
    Computes exact non-Markovian cavity dynamics beyond the Born-Markov Lindblad regime.

    Captures:
      - Memory kernel g(t) from power-law spectral density J(w) = eta * w * (w/wc)**(s-1) * exp(-w/wc)
      - Volterra integro-differential evolution for Green function u(t)
      - Time-dependent decay rate gamma(t) with quantum Zeno behavior (gamma(0) = 0)
      - Coherence and information backflow (regimes where gamma(t) < 0)
      - Time-dependent Lamb shift Delta_omega(t)
    """

    def __init__(
        self,
        name: str = "non_markovian_cavity",
        omega_r: float = 5.0,
        eta: float = 0.05,
        cutoff_wc: float = 20.0,
        spectral_s: float = 1.0,
        t_max: float = 10.0,
        n_steps: int = 500,
        n_initial: float = 1.0,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.omega_r = float(omega_r)
        self.eta = float(eta)
        self.cutoff_wc = float(cutoff_wc)
        self.spectral_s = float(spectral_s)
        self.t_max = float(t_max)
        self.n_steps = int(n_steps)
        self.n_initial = float(n_initial)
        self.temperature = float(temperature)

    def _compute_memory_kernel(self, t_grid: np.ndarray) -> np.ndarray:
        r"""
        Calculates the zero-temperature reservoir correlation kernel:
        g(t) = \int_0^\infty (dw / pi) * J(w) * exp(-i * w * t)
        """
        w_max = max(self.cutoff_wc * 8.0, 50.0)
        w_points = np.linspace(1e-4, w_max, 2000)
        dw = w_points[1] - w_points[0]

        s = self.spectral_s
        j_w = self.eta * (w_points ** s) / (self.cutoff_wc ** (s - 1.0)) * np.exp(-w_points / self.cutoff_wc)

        phase_matrix = np.exp(-1j * np.outer(t_grid, w_points))
        g_t = (phase_matrix @ j_w) * (dw / np.pi)
        return g_t

    def _solve_volterra(self, t_grid: np.ndarray, g_kernel: np.ndarray) -> np.ndarray:
        r"""
        Solves Volterra integro-differential equation for Green function u(t):
          du/dt + i * omega_r * u(t) + \int_0^t g(t - tau) u(tau) dtau = 0
          Boundary condition: u(0) = 1.0 + 0.0j
        """
        n = len(t_grid)
        dt = t_grid[1] - t_grid[0]
        u = np.zeros(n, dtype=np.complex128)
        u[0] = 1.0 + 0.0j

        for k in range(0, n - 1):
            if k == 0:
                conv_k = 0.0j
            else:
                tau_diff_indices = k - np.arange(k + 1)
                g_slice = g_kernel[tau_diff_indices]
                weights = np.ones(k + 1)
                weights[0] = 0.5
                weights[-1] = 0.5
                conv_k = np.sum(weights * g_slice * u[: k + 1]) * dt

            dudt_k = -1j * self.omega_r * u[k] - conv_k
            u_pred = u[k] + dt * dudt_k

            tau_diff_indices_next = (k + 1) - np.arange(k + 2)
            g_slice_next = g_kernel[tau_diff_indices_next]
            u_extended = np.append(u[: k + 1], u_pred)
            weights_next = np.ones(k + 2)
            weights_next[0] = 0.5
            weights_next[-1] = 0.5
            conv_next = np.sum(weights_next * g_slice_next * u_extended) * dt

            dudt_next = -1j * self.omega_r * u_pred - conv_next
            u[k + 1] = u[k] + 0.5 * dt * (dudt_k + dudt_next)

        return u

    def compute(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute non-Markovian dynamics integration.
        Accepts dynamic parameter overrides from upstream nodes.
        """
        inputs = inputs or {}
        omega_r = float(inputs.get("omega_r", self.omega_r))
        eta = float(inputs.get("eta", self.eta))
        cutoff_wc = float(inputs.get("cutoff_wc", self.cutoff_wc))
        spectral_s = float(inputs.get("spectral_s", self.spectral_s))
        t_max = float(inputs.get("t_max", self.t_max))
        n_steps = int(inputs.get("n_steps", self.n_steps))
        n_initial = float(inputs.get("n_initial", self.n_initial))

        self.omega_r = omega_r
        self.eta = eta
        self.cutoff_wc = cutoff_wc
        self.spectral_s = spectral_s

        t_grid = np.linspace(0.0, t_max, n_steps)
        dt = t_grid[1] - t_grid[0]

        # 1. Compute reservoir memory kernel
        g_kernel = self._compute_memory_kernel(t_grid)

        # 2. Integrate exact Green function u(t)
        u_t = self._solve_volterra(t_grid, g_kernel)

        # 3. Carrier-demodulated derivative for robust decay rate gamma(t)
        # u(t) = v(t) * exp(-i * omega_r * t)
        carrier = np.exp(-1j * omega_r * t_grid)
        v_env = u_t * np.exp(1j * omega_r * t_grid)
        dv_dt = np.gradient(v_env, dt)

        # Reconstructed dudt without carrier discretization artifacts
        dudt_clean = (dv_dt - 1j * omega_r * v_env) * carrier

        abs_sq = np.abs(u_t) ** 2
        safe_denom = np.where(abs_sq < 1e-14, 1e-14, abs_sq)

        # gamma(t) = -2 * Re[ (du/dt) * conj(u) ] / |u|^2
        gamma_t = -2.0 * np.real(dudt_clean * np.conj(u_t)) / safe_denom

        # Lamb shift Delta_omega(t) = -Im[ (du/dt) * conj(u) ] / |u|^2 - omega_r
        delta_omega_t = -np.imag(dudt_clean * np.conj(u_t)) / safe_denom - omega_r

        # 4. Photon number population: <a^\dagger a>(t) = |u(t)|^2 * n(0)
        pop_trace = abs_sq * n_initial

        # 5. Measure of Non-Markovianity (Breuer-Laine-Piilo / Rivas measure)
        backflow_mask = gamma_t < -1e-4
        if np.any(backflow_mask):
            non_markovianity_measure = float(np.sum(np.abs(gamma_t[backflow_mask])) * dt)
        else:
            non_markovianity_measure = 0.0

        return {
            "time_grid": t_grid,
            "green_function_u": u_t,
            "population_trace": pop_trace,
            "final_population": float(pop_trace[-1]),
            "gamma_t": gamma_t,
            "delta_omega_t": delta_omega_t,
            "coherence_factor": float(np.abs(u_t[-1])),
            "has_coherence_backflow": bool(non_markovianity_measure > 1e-4),
            "non_markovianity_measure": non_markovianity_measure,
            "zeno_initial_decay_rate": float(gamma_t[0]),
        }
