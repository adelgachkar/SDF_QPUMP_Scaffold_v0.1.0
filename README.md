# SDF QPUMP Scaffold v0.1.0

A dependency-free starter project for assembling a QPUMP computational graph. It provides a deterministic DAG runner, a small node registry, raw illustrative node implementations, JSON graph configuration, and design/calibration notes.

## Quick start

Requires Python 3.10+. From this directory, run:

```sh
python -m unittest discover -v
```

No third-party packages are required. `config/pipeline_qpump_example.json` is a declarative example. The included equations are scaffold-level phenomenological placeholders, not experimentally validated models. Check the open calibration checklist and replace/validate assumptions before scientific use.

## Graph model

Nodes implement `compute(inputs) -> outputs`; edges route a named source output to a named target input. `Graph.run(initial=...)` executes a deterministic topological ordering, passes initial node inputs and routed port values, and returns values keyed by node ID. Cycles, duplicate node IDs, invalid endpoints, and unavailable ports are reported.

See `docs/` for axiomatic framing, symbols/units, and calibration questions.
