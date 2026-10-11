# Mathematical definitions and units

This scaffold uses SI-compatible placeholders where practical. Units are **not** enforced by runtime code; configuration authors must supply consistent quantities.

| Symbol / port | Meaning | Suggested unit | Notes |
|---|---|---|---|
| `drive` | complex-mode excitation in toy cavity response | model-dependent | Current input is real-valued; extend explicitly for complex drive. |
| `detuning` | angular-frequency offset | rad s⁻¹ | Damping must use the same frequency convention. |
| `damping` | positive resonator linewidth parameter | rad s⁻¹ | Illustrative algebraic steady-state denominator. |
| `cavity_amplitude` | normalized modal response | model-dependent | `intensity = |amplitude|²`. |
| `phase_top`, `phase_bottom` | phases | rad | `phase_delta = top − bottom`. |
| `pump_thrust` | phenomenological pump output | N if calibrated as force | Raw example: gain × amplitude × sin(phase difference). |
| `berry_curvature` | curvature proxy | model-dependent | Its dimensional definition must be chosen by the application. |
| `phase_rate` | phase derivative | s⁻¹ | Bridge torque is coupling × curvature × phase rate. |
| `boundary_stress` | normal stress | Pa (N m⁻²) | `integrated_boundary_load = stress × area`, unit N. |
| `effective_metric_diagonal` | diagonal metric template | dimensionless or coordinate-dependent | Not derived from field equations; signature/convention still open. |

For reproducibility, record coordinate definitions, sign conventions, reference frame, normalization, uncertainty, and calibration dataset alongside each graph. Avoid equating the illustrative `berry_torque` or metric output with a measured physical quantity without those definitions.
