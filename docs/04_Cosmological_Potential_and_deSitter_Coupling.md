# 04. Cosmological Potential and de Sitter Boundary Coupling

## 1. Context and Objective
This document formalizes the theoretical bridge between the QPUMP effective metric source nodes, the boundary stress integrator, and background cosmic expansion dynamics. It provides a formal framework replacing a static cosmological constant ($\Lambda$) with an evolving background potential.

---

## 2. Theoretical Precedent: Minimal Dilatonic Gravity (MDG)
- **Reference:** P. Fiziev, *Cosmological Constant or Cosmological Potential*, arXiv:gr-qc/0008051v2 (34 pages).
- **Core Insights Applicable to QPUMP:**
  1. **Physical Vacuum vs. True Vacuum (pp. 17–20):**
     True vacuum corresponds to Ricci-flat Minkowski spacetime with vanishing total stress-energy. In contrast, the physical vacuum represents a non-vanishing quantum fluctuation bath generating an effective de Sitter geometry.
  2. **Dynamical Potential Replacement (pp. 4–6, 23–30):**
     Instead of an ad-hoc static constant $\Lambda$, the cosmological influence is modeled through a dynamic scalar field potential $U(\Phi)$. 
  3. **Cosmological Inversion and Inflationary Sinks (pp. 25–32):**
     Given an expansion scale factor $a(t)$, the required potential field geometry can be uniquely determined. Oscillations in the dilaton field offer non-accumulative dynamical reservoirs compatible with localized inflationary catalysts.

---

## 3. Structural Mapping to QPUMP Nodes

| MDG Mathematical Construct | QPUMP Architecture Concept | Implementation Role |
| :--- | :--- | :--- |
| Dynamic Potential $U(\Phi)$ | Non-Coherent Noise Reservoir / Scaffold | Prevents local accumulation of filtered residual energy. |
| Physical de Sitter Horizon Dilution | `EffectiveMetricSourceNode` Boundary Condition | Couples local trace energy to asymptotic background metric. |
| Scalar Curvature Coupling ($\Phi R$) | `BoundaryStressIntegratorNode` | Relates integrated boundary stresses to effective background curvature. |

---

## 4. Methodological Boundaries and Open Questions
In accordance with `docs/00_QPUMP_Axiomatic_Blueprint.md` and `docs/02_Open_Calibration_Checklist.md`:
- [ ] This reference is incorporated purely as an **analytical framework** for dynamic potential scaling.
- [ ] It does **not** constitute empirical lab-bench validation for local metric modification.
- [ ] Any pipeline implementation of non-coherent residual feedback must document the explicit functional form of the potential $U(\Phi)$ and maintain energy conservation across the boundary.
