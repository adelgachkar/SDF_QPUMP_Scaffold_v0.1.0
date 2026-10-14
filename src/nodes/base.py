from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Node(ABC):
    def __init__(self, node_id: Optional[str] = None, label: Optional[str] = None, config: Optional[Dict[str, Any]] = None, name: Optional[str] = None, **kwargs: Any) -> None:
        self.node_id = name or node_id or self.__class__.__name__
        self.label = label or self.node_id
        self.config: Dict[str, Any] = config or {}
        if kwargs:
            self.config.update(kwargs)

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.compute(inputs)

    @abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

BaseNode = Node

class PassthroughNode(Node):
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return dict(inputs)

class PlaceholderNode(Node):
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {}
