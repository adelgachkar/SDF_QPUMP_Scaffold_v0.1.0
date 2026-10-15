# Mathematical Definitions, Unit Systems, and Dimensional Mappings

## 1. Overview and Notational Conventions
This document formally defines the physical dimensions, tensorial representations, and conversion factors used throughout the QPUMP scaffold.

---

## 2. Fundamental Variables and Units

| Symbol | Physical Description | Canonical SI Unit | Scaffold Representation |
| :--- | :--- | :--- | :--- |
| $\tau$ | Causal Evolution Parameter | $\text{s}$ or dimensionless | `float` |
| $\Delta \mathcal{B}$ | Balance Discrepancy (Energy $\mathcal{E}$) | $\text{J}$ (Joules) | `float` |
| $\mathcal{F}_{\text{causal}}$ | Causal Executive Persistence (Force) | $\text{N}$ (Newtons) | `float` |
| $T_{\mu\nu}$ | Stress-Energy-Momentum Tensor | $\text{J} / \text{m}^3 \equiv \text{N}/\text{m}^2$ | `np.ndarray` $(4, 4)$ |
| $\Pi_{ij}$ | Spatial Boundary Stress Tensor | $\text{N} / \text{m}^2$ | `np.ndarray` $(3, 3)$ |
| $h_{\mu\nu}$ | Metric Perturbation ($g_{\mu\nu} - \eta_{\mu\nu}$) | Dimensionless | `np.ndarray` $(4, 4)$ |
| $R_{\text{proxy}}$ | Spacetime Curvature Proxy | $\text{m}^{-2}$ | `float` |

---

## 3. Dimensional Reduction via Causal State Evaporation

A recurring aspect of the QPUMP pipeline is the transition from conventional thermodynamic/electrodynamic quantities (e.g., optical power $P_{\text{jet}}$ in Watts, $\Pi_{ij}$ in $\text{N/m}^2$) into geometric curvature proxies ($R_{\text{proxy}}$ in $\text{m}^{-2}$ or dimensionless metric perturbations $h_{\mu\nu}$).

This is formally governed by the **Principle of Causal Evaporation**:
- Intermediate state variables represent transient causal debts during balance enforcement.
- At the integration boundary (`BoundaryStressIntegrator`), local stresses are integrated across the boundary $\partial \Omega$.
- Once the causal execution loop terminates at the `GravitationalCurvatureNode`, the microstate coordinates are integrated out ($\int_{\partial \Omega} T_{\mu\nu} d\Sigma^\nu$), leaving the metric response as the sole surviving physical remnant:
  $$G_{\mu\nu} = \kappa \langle T_{\mu\nu}^{\text{eff}} \rangle \quad \text{where} \quad \kappa = \frac{8\pi G}{c^4}$$
Therefore, dimensionality reduction from kinetic forces to geometric curvature represents an ontological projection rather than an ad-hoc normalization.
