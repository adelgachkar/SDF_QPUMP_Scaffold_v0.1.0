"""
test_laboratory_benchmarks.py
-----------------------------
Unit tests for LaboratoryBenchmarksNode (Eöt-Wash and cold-atom constraints).
"""

from src.nodes.laboratory_benchmarks import LaboratoryBenchmarksNode


def test_laboratory_benchmarks_compliant():
    node = LaboratoryBenchmarksNode()
    inputs = {
        "alpha": 1e-4,
        "screening_length": 5e-5  # 50 microns
    }
    result = node.compute(inputs)
    assert result["node_status"] == "SUCCESS"
    assert result["benchmark_eval"]["experimental_status"] == "COMPLIANT"
    assert result["benchmark_eval"]["eotwash_excluded"] is False
    assert result["benchmark_eval"]["cold_atom_excluded"] is False


def test_laboratory_benchmarks_eotwash_exclusion():
    node = LaboratoryBenchmarksNode()
    inputs = {
        "alpha": 0.5,
        "screening_length": 5e-5
    }
    result = node.compute(inputs)
    assert result["benchmark_eval"]["experimental_status"] == "EXCLUDED_BY_LABORATORY"
    assert result["benchmark_eval"]["eotwash_excluded"] is True


def test_yukawa_acceleration_ratio():
    node = LaboratoryBenchmarksNode()
    alpha = 0.1
    lambd = 1e-3
    ratio = node.yukawa_acceleration_ratio(r=lambd, alpha=alpha, lambd=lambd)
    expected = 2.0 * alpha / 2.718281828459045
    assert abs(ratio - expected) < 1e-4
