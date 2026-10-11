"""
qpump.nodes.base
==================
Base class and standard scaffolding for Q-PUMP execution nodes.
"""

from abc import ABC
from typing import Any, Dict, Optional


class Node(ABC):
    """
    Base class expected by qpump.core and NodeGraph.

    Subclasses may implement either:
    - compute(inputs), which is called by execute(), or
    - execute(inputs) directly, for backward compatibility.
    """

    def __init__(
        self,
        node_id: str,
        label: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.label = label or node_id
        self.config = dict(config or {})

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node by delegating to its compute method."""
        return self.compute(inputs)

    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses that use the compute interface."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement compute() or execute()."
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self.node_id}')>"


# نام مستعار برای سازگاری با بخش‌های دیگر پروژه
BaseNode = Node


class PassthroughNode(Node):
    """A baseline node that relays its inputs directly to outputs."""

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return dict(inputs)


class PlaceholderNode(Node):
    """A placeholder for uncalibrated or stubbed pipeline stages."""

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(inputs)
        result["status"] = "placeholder_executed"
        return result
