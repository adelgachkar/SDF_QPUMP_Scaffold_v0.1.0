"""Pytest configuration and offline stubbing for SDF QPUMP Scaffold."""
import sys
import os
from unittest.mock import MagicMock

# اطمینان از قرار گرفتن ریشه پروژه در sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# فال‌بک خودکار برای networkx در محیط آفلاین
try:
    import networkx
except ImportError:
    class FakeDiGraph:
        def __init__(self, *args, **kwargs):
            self._nodes = {}
            self._edges = []
        def add_node(self, n, **attr):
            self._nodes[n] = attr
        def add_edge(self, u, v, **attr):
            self._edges.append((u, v, attr))
        def nodes(self):
            return list(self._nodes.keys())
        def edges(self):
            return self._edges

    fake_nx = MagicMock()
    fake_nx.DiGraph = FakeDiGraph
    fake_nx.Graph = FakeDiGraph
    fake_nx.__version__ = "stub-offline"
    sys.modules["networkx"] = fake_nx
