# QPUMP axiomatic blueprint (scaffold)

## Purpose and epistemic status
QPUMP is organized here as a modular graph in which independently authored nodes exchange named quantities. This document is an engineering blueprint, not a claim that the proposed physics is experimentally established. The node equations in this release are deliberately raw examples.

## Working principles
1. **Explicit contracts:** each node declares a stable type name and computes a mapping of named outputs from inputs.
2. **Causal execution:** edges define data dependencies; execution is deterministic and acyclic.
3. **Traceable assumptions:** parameters, unit conventions, and calibration status should be recorded with every model revision.
4. **Separation of layers:** cavity response, pump conversion, Berry bridge, boundary integration, and effective-metric representation remain separate modules.
5. **No hidden validation:** a computed value is not evidence of a physical effect; compare predictions to calibrated data and uncertainty budgets.

## Suggested path
Start with a measured resonator transfer function, determine phase and amplitude conventions, calibrate pump gain and load, then test any Berry-curvature coupling independently. Derive metric mappings only after independently validated stress/geometry relations exist. Preserve raw observables alongside transformed model quantities.

## Graph contract
Each edge carries one named output to one named input. A node may have multiple upstream inputs. Cycles are rejected in this scaffold; stateful feedback requires a separately specified time-stepping interface.
