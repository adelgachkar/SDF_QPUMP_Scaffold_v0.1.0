"""
qpump.quantum_geometry
=======================
Geometric phases, Berry curvature, and Quantum Geometric Tensor (QGT)
for QPUMP gauge and peristaltic physics.
"""
import math
from typing import Dict, Tuple, Any


class QuantumGeometryEngine:
    """
    Computes Berry connection, curvature, and Provost-Vallee metric
    for a parameterized two-level quantum pump model.
    """
    
    @staticmethod
    def two_level_berry_curvature(
        bx: float, by: float, bz: float
    ) -> Tuple[float, float]:
        """
        Calculates Berry curvature and quantum metric for a Monopole-like
        spin-1/2 hamiltonian H = Bx*sigma_x + By*sigma_y + Bz*sigma_z.
        Returns (berry_curvature_z, quantum_metric_trace).
        """
        r2 = bx * bx + by * by + bz * bz
        r = math.sqrt(r2)
        if r < 1e-12:
            return 0.0, 0.0
        # Berry curvature over sphere: F = -0.5 * bz / (r^3)
        f = -0.5 * bz / (r2 * r)
        gtrace = 0.5 / r2
        return f, gtrace

    @staticmethod
    def adiabatic_pump_cycle(
        amplitude: float,
        detuning: float,
        cycles_n: float = 1.0
    ) -> Dict[str, float]:
        """
        Simulates a closed circular parameter loop in (bx, by) at fixed bz
        to compute total accumulated geometric (Berry) phase and torque.
        """
        bz_safe = max(abs(detuning), 1e-6) * (1.0 if detuning >= 0 else -1.0)
        r0 = math.sqrt(amplitude * amplitude + bz_safe * bz_safe)
        
        # Solid angle subtended by the loop on the bloch sphere:
        cos_theta = bz_safe / r0
        solid_angle = 2.0 * math.pi * (1.0 - cos_theta)
        geometric_phase = -0.5 * solid_angle * cycles_n
        
        # Geometric Torque
        torque = 0.5 * math.sin(math.acos(max(-1.0, min(1.0, cos_theta)))) * amplitude
        
        return {
            "berry_phase_rad": geometric_phase,
            "solid_angle_sr": solid_angle,
            "geometric_torque": torque,
            "quantum_metric_trace": 1.0 / (2.0 * r0 * r0),
        }

    @staticmethod
    def non_adiabatic_correction(
        omega_drive: float,
        energy_gap: float
    ) -> float:
        """
        Dykhne-Davis-Pechukas non-adiabatic transition probability.
        """
        if energy_gap <= 1e-6:
            return 1.0
        adiabatic_param = omega_drive / energy_gap
        if adiabatic_param <= 0.0:
            return 0.0
        pi_float = math.pi * energy_gap / (2.0 * max(omega_drive, 1e-9))
        if -pi_float < -70.0:
            return 0.0
        return math.exp(-pi_float)
