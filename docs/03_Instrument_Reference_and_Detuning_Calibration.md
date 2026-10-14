# 03. Instrument Reference and Resonator Detuning Calibration

## 1. Scope and Boundary Definition
This document provides an engineering instrumentation reference for measuring cavity frequency shifts, establishing sample baseline tracking, and handling detuning inputs within the QPUMP software framework.

**Explicit Scope Boundary:**
- **Valid Applicability:** Classical frequency counting, baseline drift mitigation (auto-zeroing), and empirical monitoring of resonator detuning ($\Delta \omega$) in low-frequency proxy test benches.
- **Excluded Applicability:** This document does not provide experimental validation for Berry phase curvature, metric perturbations, quantum vacuum states, non-coherent noise catalysts, or propulsion/thrust generation.

---

## 2. Cited Engineering Precedent
- **Source:** *Design of a Beat Frequency Oscillator Metal Detector* (Pages 1–7).
- **Architecture Examined:**
  1. **Oscillator Stage:** An LC-based resonant tank where external perturbations alter the effective component parameters (inductance/capacitance), shifting the oscillation frequency.
  2. **Frequency Acquisition:** Digital counting of sensor pulses over fixed acquisition windows ($\approx 250\text{ ms}$, corresponding to $\approx 4\text{ Hz}$ update rate).
  3. **Baseline Auto-Zeroing:** Mitigation of slow thermal drift by continuously averaging samples and establishing a new operational baseline when 16 consecutive measurements remain stationary.

---

## 3. Mapping to QPUMP Nodes

In `docs/00_QPUMP_Axiomatic_Blueprint.md` and `docs/01_Mathematical_Definitions_and_Units.md`, the `CavityResonatorNode` requires a parameter defined as `detuning`:

$$\Delta \omega = \omega_{\text{drive}} - \omega_0$$

The instrumentation precedent maps to the pipeline as follows:

| Hardware/Instrumentation Mechanism | QPUMP Node Parameter | Functional Role |
| :--- | :--- | :--- |
| Perturbed LC Oscillator Output | `detuning` (rad/s or Hz) | Feeds measured frequency deviation from cavity resonance. |
| 250 ms Timer Measurement Gate | Time-step aggregation ($\Delta t$) | Dictates discrete update rate for sequential pipeline runs. |
| 16-sample stability zeroing | Environmental drift baseline | Decouples environmental thermal drift from intentional cavity drive signals. |

---

## 4. Verification and Validation Checklist Additions
In accordance with `docs/02_Open_Calibration_Checklist.md`, any hardware adapter or data-ingestion node derived from this method must satisfy:

- [ ] **Transfer Function Verification:** Independent calibration of coil/cavity geometry vs. frequency response curve.
- [ ] **Null-Drive Test:** Verification that baseline tracking settles to zero when no active drive perturbation is applied.
- [ ] **Thermal Decoupling:** Confirmation that the 16-sample auto-zero threshold differentiates between ambient thermal drift and drive-induced phase shifts.
- [ ] **Unit Consistency:** Transformation of digital counter outputs (Hz / discrete counts) into the dimensioned units required by the processing pipeline before node execution.
