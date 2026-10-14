# 05. Differential Geometric Methods for Boundary Surfaces and Cavity Envelopes

## 1. Context and Architectural Purpose
In the `SDF_QPUMP_Scaffold_v0.1.0` architecture, computing stress tensors across resonant cavities and boundary shells requires rigorous geometric formulations. The `BoundaryStressIntegratorNode` computes scalar and tensor projections across non-trivial geometric enclosures. This document establishes the mathematical foundation for surface curvatures, contact tangency, and metric degenerate handling based on computational differential geometry.

---

## 2. Theoretical Reference
- **Source:** F.-E. Wolter, *Differential Geometric Methods in Geometric Modeling*, Leibniz University Hannover (52 slides).
- **Core Mathematical Principles Applied to QPUMP:**

### A. Three Tangents Theorem and Contact Order (Slides 4–12)
- **Mathematical Statement:** For two regular surfaces in tangential contact at point $P$, equality of normal curvatures along three linearly independent tangent directions implies identical second fundamental forms:
  $$b_{ij}^{(1)} = b_{ij}^{(2)}$$
- **QPUMP Pipeline Application:**
  - Guarantees $C^2$ smoothness and continuous phase boundary conditions where discrete tetrahedral cavity cells intersect.
  - Used in verifying harmonic boundary compatibility without inducing numerical edge singular artifacts in the field integrator.

### B. Regularization of Degenerate Parameterizations (Slides 14–24)
- **Mathematical Formulation:** When parametric coordinate representations suffer rank deficiency, metric components $g_{ij}$ become singular. The local geometry is regularized via height-function representations over the tangent plane:
  $$K = \frac{\det(b_{ij})}{\det(g_{ij})}, \quad H = \frac{1}{2} g^{ij} b_{ij}$$
- **QPUMP Pipeline Application:**
  - Robust evaluation of Gaussian ($K$) and Mean ($H$) curvatures at geometric poles, vertices, and junction seams of the 5-tetrahedral scaffold.
  - Prevents division-by-zero exceptions in discrete metric calculators.

### C. Orthogonal Projections and Distance Trajectories (Slides 25–42)
- **Mathematical Tools:** Differential equations tracking normal footpoints and cut-locus topological boundaries using gradient field rotation indices.
- **QPUMP Pipeline Application:**
  - Determines boundary-layer distances for exponential field decay and evanescent mode attenuation within `CavityResonatorNode`.

---

## 3. Structural Mapping to QPUMP Nodes

| Geometric Concept (Wolter) | Mathematical Construct | Target Scaffold Component |
| :--- | :--- | :--- |
| First Fundamental Form | Metric Tensor $g_{ij} = \langle \partial_i S, \partial_j S \rangle$ | Local surface metric scaling in `BoundaryStressIntegratorNode` |
| Second Fundamental Form | Curvature Tensor $b_{ij} = \langle \partial_{ij} S, N \rangle$ | Boundary normal stress projection |
| Three Tangents Theorem | Contact Order $C^2$ matching | Tetrahedral cluster seam continuity validation |
| Cut-Locus / Footpoint Tracking | $\dot{x}(t) = \nabla d(x(t))$ | Resonator cavity wall proximity calculations |

---

## 4. Scope and Explicit Scientific Boundaries
In alignment with `docs/00_QPUMP_Axiomatic_Blueprint.md` and `docs/02_Open_Calibration_Checklist.md`:
- [ ] This reference is strictly a **computational mathematics and CAGD framework** for spatial 2-surfaces in $\mathbb{R}^3$.
- [ ] It does **not** provide empirical or relativistic evidence for spacetime metric manipulation ($g_{\mu\nu}$) or physical quantum Berry phase.
- [ ] Any node implementing these equations must verify regular surface criteria and isolate purely spatial cavity integration from effective gravitational coupling pipelines.
