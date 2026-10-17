# Dimensional Gap Resolution and Substrate Metric Correspondence

## 1. Purpose and Scope
This document formalizes how the QPUMP (Quantum Peristaltic Unified Modulation Pipeline) scaffold bridges the **dimensional gap** between non-equilibrium electromagnetic stress quantities (Watts, Pascals) and geometric observables (metric perturbations $h_{\mu\nu}$, curvature proxies $R_{\text{proxy}}$ in $\text{m}^{-2}$). It also defines the **substrate metric correspondence**: the explicit mapping between the computational substrate (lattice / tensor arrays / solver states) and the effective Lorentzian geometry reconstructed from them.

This document extends:
- `00_QPUMP_Axiomatic_Blueprint.md` (Axioms 1–3, metric residue)
- `01_Mathematical_Definitions_and_Units.md` (unit table, dimensional reduction)
- `04_Cosmological_Potential_and_deSitter_Coupling.md` (de Sitter curvature scale)
- `05_Differential_Geometric_Methods_for_Boundary_Surfaces.md` (boundary stress geometry)

---

## 2. The Dimensional Gap

### 2.1 Definition
The dimensional gap $\mathcal{G}_{\text{dim}}$ is the formal discrepancy between the **stress sector** and the **geometric sector** of the pipeline:

$$
\mathcal{G}_{\text{dim}} \;:\; \Pi_{ij}\ [\text{N}/\text{m}^2],\ P_{\text{jet}}\ [\text{W}] \;\not\Longleftrightarrow\; h_{\mu\nu}\ [-],\ R_{\text{proxy}}\ [\text{m}^{-2}]
$$

Stress carries dimension $\text{kg}\cdot\text{m}^{-1}\cdot\text{s}^{-2}$; curvature carries $\text{m}^{-2}$. No algebraic equality exists without a conversion postulate.

### 2.2 Gap Resolution Postulate (Extension of Axiom 3)
QPUMP resolves the gap through a **Causal State Evaporation conversion postulate**: microstate thermodynamic quantities decohere and are traced out; the sole surviving macroscopic observable is a metric residue. The conversion is fixed by a single coupling scale $\lambda_{\text{G}}$:

$$
R_{\text{proxy}} \;=\; \lambda_{\text{G}} \cdot \frac{8\pi G}{c^4}\, \Pi_{\text{eff}}
\qquad\text{with}\qquad
[\lambda_{\text{G}}] = \text{N}
$$

where $\Pi_{\text{eff}} \equiv \operatorname{tr}(\Pi_{ij})/3$ is the isotropic boundary stress invariant. The factor $(8\pi G/c^4)$ is the Einstein stress-to-curvature kernel; $\lambda_{\text{G}}$ absorbs all untraced microstate degrees of freedom and is an **open calibration constant** (see `02_Open_Calibration_Checklist.md`).

### 2.3 Derived Metric Perturbation
In the weak-field limit, the trace-reversed metric perturbation $\bar{h}_{\mu\nu}$ obeys the linearized correspondence:

$$
\bar{h}_{\mu\nu} \;=\; \frac{2}{R_{\text{S}}}\,\mathcal{L}^{-1}\!\left[\frac{8\pi G}{c^4} T_{\mu\nu}\right],
\qquad
h_{\mu\nu} = \bar{h}_{\mu\nu} - \tfrac{1}{2}\eta_{\mu\nu}\bar{h}
$$

where $\mathcal{L}^{-1}$ denotes the Green-function inverse of the flat-space d'Alembertian on the causal boundary surface, and $R_{\text{S}}$ is the characteristic curvature radius of the cavity substrate.

---

## 3. Substrate Metric Correspondence

### 3.1 The Substrate
The **substrate** is the discrete computational manifold on which the QPUMP solver operates:
- a $(3+1)$ lattice with spacing $\Delta x$, time step $\Delta t$ satisfying the CFL condition $\Delta t \le \Delta x / (c\sqrt{d})$;
- state fields stored as `np.ndarray` objects per the unit table in `01_Mathematical_Definitions_and_Units.md`.

### 3.2 Correspondence Map $\Phi$
The substrate-to-geometry correspondence map $\Phi$ assigns to every substrate state an effective metric:

$$
\Phi:\ \{ \Pi_{ij},\ P_{\text{jet}},\ \mathcal{E} \}_{\text{substrate}}
\;\longmapsto\;
g^{\text{eff}}_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}(\Pi_{\text{eff}}, \lambda_{\text{G}})
$$

**Correspondence conditions (must all hold):**

1. **Consistency (Einstein constraint):** the reconstructed $g^{\text{eff}}_{\mu\nu}$ must reproduce the injected stress tensor up to the calibration scale:
   $$G_{\mu\nu}[g^{\text{eff}}] \approx \lambda_{\text{G}}\, T_{\mu\nu}$$
2. **Trace preservation:** $\operatorname{tr}(\Pi_{ij}) \mapsto -R_{\text{proxy}}\, c^4/(8\pi G \lambda_{\text{G}})$ — no residual dimensionless debt beyond the evaporation residue.
3. **Causality:** the light cones of $g^{\text{eff}}_{\mu\nu}$ must contain the substrate CFL cones; effective metric refractivity $n_{\text{eff}} = \sqrt{g^{\text{eff}}_{00}} \ge 1$.
4. **Gauge residue:** only gauge-invariant scalars ($R_{\text{proxy}}$, $\bar{h}$, $\Pi_{\text{eff}}$) are propagated across $\Phi$; gauge-dependent components are evaporated.

### 3.3 Discrete Curvature Operator
On the substrate lattice, the curvature proxy is computed by the discrete scalar-curvature operator (consistent discretization of `05`):

$$
R_{\text{proxy}}^{(k)} = \sum_{\mu,\nu} \Delta_\mu \Gamma^\mu_{\nu\nu} - \Delta_\nu \Gamma^\nu_{\mu\nu}
$$

with Christoffel symbols assembled from central differences of $h_{\mu\nu}$ and $\Gamma$ vanishing on unperturbed boundary nodes. Residual lattice error scales as $\mathcal{O}(\Delta x^2)$ and must be reported in solver diagnostics.

---

## 4. Numerical Workflow

| Step | Operation | Input → Output | Unit Check |
| :--- | :--- | :--- | :--- |
| 1 | Collect boundary stress | $\Pi_{ij}$ `np.ndarray (3,3)` [$\text{N/m}^2$] | trace → $\text{N/m}^2$ |
| 2 | Evaporate microstates | trace-out over internal DOF | dimensionless weight $w\in[0,1]$ |
| 3 | Apply kernel | $R_{\text{proxy}} = \lambda_{\text{G}} (8\pi G/c^4)\Pi_{\text{eff}}$ | → $\text{m}^{-2}$ |
| 4 | Invert Green function | $\mathcal{L}^{-1}$ on $\bar{h}_{\mu\nu}$ | dimensionless |
| 5 | Reconstruct metric | $g^{\text{eff}}_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu}$ | dimensionless |
| 6 | Verify constraints | Sec. 3.2 conditions 1–4 | residuals < tolerance |

**Reference magnitudes** (for sanity checks with $\lambda_{\text{G}} = 1\ \text{N}$):

$$
\frac{8\pi G}{c^4} \approx 2.077 \times 10^{-43}\ \text{s}^2/(\text{kg}\cdot\text{m})
\;\Rightarrow\;
R_{\text{proxy}} \approx 2.077 \times 10^{-43}\, \Pi_{\text{eff}}[\text{Pa}]\ \text{m}^{-2}
$$

A cavity boundary stress of $\Pi_{\text{eff}} = 10^{9}\ \text{Pa}$ yields $R_{\text{proxy}} \sim 2\times10^{-34}\ \text{m}^{-2}$ — far below the de Sitter background scale unless $\lambda_{\text{G}} \gg 1\ \text{N}$. This is the quantitative statement of the dimensional gap and motivates the open calibration of $\lambda_{\text{G}}$ in `02_Open_Calibration_Checklist.md`.

---

## 5. Minimal Reference Implementation

```python
import numpy as np

G     = 6.67430e-11      # m^3 kg^-1 s^-2
C     = 2.99792458e8     # m/s
LAMBDAG = 1.0            # N  (open calibration constant)

def curvature_proxy(Pi: np.ndarray, lambda_G: float = LAMBDAG) -> float:
    """Step 3: stress tensor (N/m^2) -> curvature proxy (m^-2)."""
    Pi_eff = np.trace(Pi) / 3.0
    return lambda_G * (8.0 * np.pi * G / C**4) * Pi_eff

def metric_perturbation(R_proxy: float, R_S: float) -> float:
    """Isotropic weak-field trace: h ~ -R_proxy * R_S^2 / 12 (order of magnitude)."""
    return -R_proxy * R_S**2 / 12.0

def substrate_metric(Pi: np.ndarray, R_S: float,
                     lambda_G: float = LAMBDAG) -> np.ndarray:
    """Steps 3-5: boundary stress -> effective metric g_eff (4,4)."""
    R = curvature_proxy(Pi, lambda_G)
    h = metric_perturbation(R, R_S)
    g_eff = np.eye(4) * np.array([-1.0, 1.0, 1.0, 1.0]) + h * np.eye(4)
    return g_eff
```

**Validation invariants** (assert in tests):
- `curvature_proxy(np.eye(3)*Pi0) == lambda_G * (8πG/c^4) * Pi0` exactly.
- `g_eff` symmetric; deviation of $g^{\text{eff}}_{00}$ from $-1$ has magnitude $|h| \ll 1$ in the weak-field regime.
- CFL condition holds before any $\mathcal{L}^{-1}$ application.

---

## 6. Open Items
1. Calibration of $\lambda_{\text{G}}$ against measured cavity detuning data (`03_Instrument_Reference_and_Detuning_Calibration.md`).
2. Lattice-convergence study of $R_{\text{proxy}}^{(k)}$ vs. $\Delta x$ (target: second-order scaling demonstrated on a boundary-surface benchmark).
3. Consistency of the correspondence map $\Phi$ with the de Sitter coupling of `04` at cosmological stress scales.
4. Gauge-fixing convention for the trace-reversed potential $\bar{h}_{\mu\nu}$ (harmonic gauge assumed here).

---

*Scaffold version: v0.1.0 — Document 09. All constants are CODATA-consistent; $\lambda_{\text{G}}$ is a scaffold-internal calibration parameter, not a measured physical constant.*
