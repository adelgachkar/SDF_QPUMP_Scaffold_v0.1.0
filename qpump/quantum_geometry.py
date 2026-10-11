"""
qpump.quantum_geometry
=======================
Berry curvature, quantum geometric tensor (QGT), and dynamics.
"""

from typing import Tuple, Dict, Any
import numpy as np


def quantum_geometric_tensor_two_level(
    bx: float, by: float, bz: float
) -> np.ndarray:
    """Computes QGT for spin-1/2 hamiltonian."""
    r = float(np.sqrt(bx**2 + by**2 + bz**2))
    if r < 1e-15:
        return np.zeros((3, 3), dtype=complex)
    g = np.eye(3, dtype=float) / (4.0 * r**2)
    Fxy = -0.5 * bz / (r**3)
    Fyz = -0.5 * bx / (r**3)
    Fzx = -0.5 * by / (r**3)
    F_tensor = np.array(
        [
            [0.0, Fxy, -Fzx],
            [-Fxy, 0.0, Fyz],
            [Fzx, -Fyz, 0.0],
        ],
        dtype=float,
    )
    return g - 0.5j * F_tensor


def berry_curvature_from_qgt(QGT: np.ndarray) -> np.ndarray:
    """Extracts Berry curvature vector from imaginary part of QGT."""
    F_tensor = -2.0 * np.imag(QGT)
    return np.array([F_tensor[1, 2], F_tensor[2, 0], F_tensor[0, 1]], dtype=float)


def geometric_torque_from_berry(
    berry_curvature: np.ndarray,
    parameter_velocity: np.ndarray,
    hbar: float = 1.054571817e-34,
) -> np.ndarray:
    """Tau = hbar * (v x Omega)"""
    return hbar * np.cross(parameter_velocity, berry_curvature)


def dykhne_davis_pechukas_transition_rate(
    gap_min: float,
    drive_rate: float,
    hbar: float = 1.054571817e-34,
) -> float:
    """Transition probability due to non-adiabatic excitation."""
    if drive_rate <= 1.0e-20:
        return 0.0
    argument = -np.pi * (gap_min**2) / (2.0 * hbar * drive_rate)
    return float(np.exp(np.clip(argument, -100.0, 0.0)))


class QuantumGeometryEngine:
    """Engine for higher-level quantum geometry and adiabatic pump operations."""

    @staticmethod
    def two_level_berry_curvature(bx: float, by: float, bz: float) -> Tuple[float, float]:
        r = float(np.sqrt(bx**2 + by**2 + bz**2))
        if r < 1e-15:
            return 0.0, 0.0
        # Berry curvature for monopole (negative sign for ground state / north pole)
        f_z = -0.5 * bz / (r**3)
        gtrace = 1.0 / (2.0 * (r**2))
        return float(f_z), float(gtrace)

    @staticmethod
    def adiabatic_pump_cycle(
        amplitude: float, detuning: float, cycles_n: float = 1.0
    ) -> Dict[str, Any]:
        r = float(np.sqrt(amplitude**2 + detuning**2))
        if r < 1e-15:
            return {"berry_phase_rad": 0.0, "geometric_torque": [0.0, 0.0, 0.0]}
        solid_angle = 2.0 * np.pi * (1.0 - detuning / r)
        phase = float(cycles_n * solid_angle)
        return {
            "berry_phase_rad": phase,
            "geometric_torque": [0.0, 0.0, float(0.1 * phase)],
        }
