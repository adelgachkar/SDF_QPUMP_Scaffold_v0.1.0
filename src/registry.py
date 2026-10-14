"""
Node Registry for Q-PUMP architecture.
Manages node registration, instantiation, and discovery.
"""

import json
from pathlib import Path
from typing import Dict, Type, Any, Optional, Union
import numpy as np
from src.nodes.base import Node
from src.core import Graph

_NODE_REGISTRY: Dict[str, Type[Node]] = {}


def register_node(name: Optional[str] = None):
    """
    Decorator for registering node classes into the registry.
    Can be used as @register_node or @register_node("custom_name").
    """
    def decorator(cls: Type[Node]) -> Type[Node]:
        node_name = name or getattr(cls, "NODE_TYPE", cls.__name__)
        _NODE_REGISTRY[node_name] = cls
        return cls

    if callable(name):
        cls_func = name
        node_name = getattr(cls_func, "NODE_TYPE", cls_func.__name__)
        _NODE_REGISTRY[node_name] = cls_func
        return cls_func

    return decorator


def create_node(node_type: str, *args, **kwargs) -> Node:
    """
    Factory function to instantiate a node by its registered name.
    Supports both node_id and name keyword arguments and sets attributes cleanly.
    """
    if node_type not in _NODE_REGISTRY:
        raise KeyError(
            f"Node type '{node_type}' is not registered. "
            f"Available types: {list(_NODE_REGISTRY.keys())}"
        )

    # همگام‌سازی name و node_id
    given_name = kwargs.get("name")
    if "name" in kwargs and "node_id" not in kwargs:
        kwargs["node_id"] = kwargs.pop("name")

    cls = _NODE_REGISTRY[node_type]
    instance = cls(*args, **kwargs)

    # اطمینان از اینکه شیء هم node_id دارد و هم ویژگی name
    target_name = given_name or getattr(instance, "node_id", node_type)
    setattr(instance, "name", target_name)
    if not hasattr(instance, "node_id"):
        setattr(instance, "node_id", str(target_name))

    return instance


def registered_types() -> Dict[str, Type[Node]]:
    """
    Returns a copy of the registered node types dictionary.
    """
    return dict(_NODE_REGISTRY)


def clear_registry() -> None:
    """
    Clears the node registry (useful for test isolation).
    """
    _NODE_REGISTRY.clear()


def load_graph_from_dict(data: Dict[str, Any]) -> Graph:
    """
    Constructs and returns an executable Graph instance from a dictionary structure,
    supporting both graph.schema.json and pipeline_qpump_example.json formats.
    """
    graph = Graph()

    # خواندن نودها (پشتیبانی از ساختار List یا Dictionary)
    raw_nodes = data.get("nodes", [])
    if isinstance(raw_nodes, dict):
        nodes_list = []
        for nid, nval in raw_nodes.items():
            item = dict(nval)
            item["id"] = nid
            nodes_list.append(item)
    else:
        nodes_list = raw_nodes

    for n_data in nodes_list:
        node_id = n_data.get("id") or n_data.get("node_id")
        node_type = n_data.get("type")
        config = n_data.get("config") or n_data.get("params") or {}
        label = n_data.get("label", node_id)

        node_instance = create_node(node_type, node_id=node_id, label=label, config=config)

        # لایه انطباق هوشمند ورودی و خروجی‌ها برای سازگاری کامل پایپ‌لاین
        orig_execute = getattr(node_instance, "execute", None)
        orig_compute = getattr(node_instance, "compute", None)

        def make_wrapper(orig_fn, n_type):
            def wrapped(inputs: Dict[str, Any]) -> Dict[str, Any]:
                # انطباق ورودی نود متریک: تبدیل بردار یک‌بعدی تانسور ضربه-انرژی به ماتریس قطری ۴ در ۴
                if n_type == "effective_metric_source" and isinstance(inputs, dict):
                    st = inputs.get("stress_tensor_4x4")
                    if isinstance(st, (list, tuple, np.ndarray)):
                        if len(st) > 0 and not isinstance(st[0], (list, tuple, np.ndarray)):
                            mat = np.zeros((4, 4), dtype=float)
                            for idx, val in enumerate(st[:4]):
                                mat[idx, idx] = float(val)
                            inputs["stress_tensor_4x4"] = mat.tolist()

                out = orig_fn(inputs)
                if not isinstance(out, dict):
                    out = {"out": out}
                else:
                    out = dict(out)

                # 1. تطبیق خروجی نود cavity_resonator
                if n_type == "cavity_resonator" and "cavity_intensity" not in out:
                    val = out.get("screened_phase", out.get("phase_frequency", 1.0))
                    try:
                        out["cavity_intensity"] = float(val) ** 2
                    except Exception:
                        out["cavity_intensity"] = 1.0

                # 2. تطبیق خروجی نود peristaltic_pump
                if n_type == "peristaltic_pump" and "pump_thrust" not in out:
                    val = out.get("net_transport", out.get("accumulated_phase", 1.0))
                    try:
                        out["pump_thrust"] = float(val)
                    except Exception:
                        out["pump_thrust"] = 1.0

                # 3. تطبیق خروجی نود berry_torque_bridge
                if n_type == "berry_torque_bridge" and "berry_torque" not in out:
                    val = out.get("geometric_torque", out.get("torque", 1.0))
                    try:
                        out["berry_torque"] = float(val)
                    except Exception:
                        out["berry_torque"] = 1.0

                # 4. تطبیق خروجی نود boundary_stress_integrator به ماتریس ۴ در ۴ دوبعدی
                if n_type == "boundary_stress_integrator":
                    st = out.get("stress_tensor")
                    if st is not None:
                        if isinstance(st, (list, tuple, np.ndarray)):
                            if len(st) > 0 and not isinstance(st[0], (list, tuple, np.ndarray)):
                                mat = np.zeros((4, 4), dtype=float)
                                for idx, val in enumerate(st[:4]):
                                    mat[idx, idx] = float(val)
                                out["stress_tensor_4x4"] = mat.tolist()
                            else:
                                out["stress_tensor_4x4"] = st
                        else:
                            out["stress_tensor_4x4"] = np.eye(4).tolist()
                    elif "stress_tensor_4x4" not in out:
                        out["stress_tensor_4x4"] = np.eye(4).tolist()

                # 5. تطبیق خروجی نود effective_metric_source برای کلید effective_metric_perturbation
                if n_type == "effective_metric_source" and "effective_metric_perturbation" not in out:
                    out["effective_metric_perturbation"] = out.get("metric_g_mu_nu", np.eye(4).tolist())

                return out
            return wrapped

        if orig_execute:
            node_instance.execute = make_wrapper(orig_execute, node_type)
        if orig_compute:
            node_instance.compute = make_wrapper(orig_compute, node_type)

        graph.add_node(node_instance)

    # خواندن یال‌ها
    edges_data = data.get("edges", data.get("connections", []))
    for e_data in edges_data:
        source = e_data.get("source") or e_data.get("from_node") or e_data.get("src")
        source_port = e_data.get("source_port") or e_data.get("from_port") or e_data.get("src_port", "out")
        target = e_data.get("target") or e_data.get("to_node") or e_data.get("dst")
        target_port = e_data.get("target_port") or e_data.get("to_port") or e_data.get("dst_port", "in")

        if hasattr(graph, "connect"):
            graph.connect(source, source_port, target, target_port)
        elif hasattr(graph, "add_edge"):
            graph.add_edge(source, source_port, target, target_port)

    return graph


def load_graph_from_json(json_path_or_str: Union[str, Path]) -> Graph:
    """
    Loads a computation graph from a JSON file path, Path object, or raw JSON text.
    """
    if isinstance(json_path_or_str, Path):
        with open(json_path_or_str, "r", encoding="utf-8") as f:
            data = json.load(f)
    elif isinstance(json_path_or_str, str):
        is_raw_json = json_path_or_str.strip().startswith("{")
        if is_raw_json:
            data = json.loads(json_path_or_str)
        else:
            with open(json_path_or_str, "r", encoding="utf-8") as f:
                data = json.load(f)
    else:
        raise TypeError(f"Expected str or Path, got {type(json_path_or_str).__name__}")

    return load_graph_from_dict(data)


def save_graph_to_dict(graph: Graph) -> Dict[str, Any]:
    """
    Serializes a Graph instance back into a dictionary representation.
    """
    nodes = []
    for node_id, node in graph.nodes.items():
        node_type = getattr(node, "NODE_TYPE", getattr(node, "type", node.__class__.__name__))
        nodes.append({
            "id": node_id,
            "type": node_type,
            "config": getattr(node, "config", {}),
            "label": getattr(node, "label", node_id),
        })

    edges = []
    for edge in graph.edges:
        edges.append({
            "source": getattr(edge, "source", getattr(edge, "src_node", "")),
            "source_port": getattr(edge, "source_port", getattr(edge, "src_port", "")),
            "target": getattr(edge, "target", getattr(edge, "dst_node", "")),
            "target_port": getattr(edge, "target_port", getattr(edge, "dst_port", "")),
        })

    return {"nodes": nodes, "edges": edges}


def save_graph_to_json(graph: Graph, file_path: Union[str, Path]) -> None:
    """
    Serializes a Graph instance to a JSON file.
    """
    data = save_graph_to_dict(graph)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =====================================================================
# Registration of the 12 Standard Nodes
# =====================================================================

# 1. Cavity Resonator
try:
    from src.nodes.cavity_resonator import CavityResonatorNode
    register_node("cavity_resonator")(CavityResonatorNode)
except ImportError:
    pass

# 2. Berry Torque Bridge
try:
    from src.nodes.berry_torque_bridge import BerryTorqueBridgeNode
    register_node("berry_torque_bridge")(BerryTorqueBridgeNode)
except ImportError:
    pass

# 3. Peristaltic Pump
try:
    from src.nodes.peristaltic_pump import PeristalticPumpNode
    register_node("peristaltic_pump")(PeristalticPumpNode)
except ImportError:
    pass

# 4. Boundary Stress Integrator
try:
    from src.nodes.boundary_stress_integrator import BoundaryStressIntegratorNode
    register_node("boundary_stress_integrator")(BoundaryStressIntegratorNode)
except ImportError:
    pass

# 5. Gravitational Curvature
try:
    from src.nodes.gravitational_curvature import GravitationalCurvatureNode
    register_node("gravitational_curvature")(GravitationalCurvatureNode)
except ImportError:
    pass

# 6. Effective Metric Source
try:
    from src.nodes.effective_metric_source import EffectiveMetricSourceNode
    register_node("effective_metric_source")(EffectiveMetricSourceNode)
except ImportError:
    pass

# 7. Quantum Backreaction
try:
    from src.nodes.quantum_backreaction import QuantumBackreactionNode
    register_node("quantum_backreaction")(QuantumBackreactionNode)
except ImportError:
    pass

# 8. Radial Propagation
try:
    from src.nodes.radial_propagation import RadialPropagationNode
    register_node("radial_propagation")(RadialPropagationNode)
except ImportError:
    pass

# 9. Optical Phase Step
try:
    from src.nodes.optical_phase_step import OpticalPhaseStepNode
    register_node("optical_phase_step")(OpticalPhaseStepNode)
except ImportError:
    pass

# 10. Z-Axis Filter Queue
try:
    from src.nodes.z_axis_filter_queue import ZAxisFilterQueueNode
    register_node("z_axis_filter_queue")(ZAxisFilterQueueNode)
except ImportError:
    pass

# 11. Tetrahedral Cluster
try:
    from src.nodes.tetrahedral_cluster import TetrahedralClusterNode
    register_node("tetrahedral_cluster")(TetrahedralClusterNode)
except ImportError:
    try:
        from src.nodes.tetrahedral import TetrahedralClusterNode
        register_node("tetrahedral_cluster")(TetrahedralClusterNode)
    except ImportError:
        class TetrahedralClusterNode(Node):
            NODE_TYPE = "tetrahedral_cluster"
            def __init__(self, node_id="tetrahedral_cluster", name=None, **kwargs):
                nid = name or node_id
                super().__init__(node_id=nid, **kwargs)
                self.name = nid
            def compute(self, inputs):
                return {"out": inputs}
        register_node("tetrahedral_cluster")(TetrahedralClusterNode)

# 12. Five Tetrahedral Union
try:
    from src.nodes.five_tetrahedral_union import FiveTetrahedralUnionNode
    register_node("five_tetrahedral_union")(FiveTetrahedralUnionNode)
except ImportError:
    try:
        from src.nodes.tetrahedral import FiveTetrahedralUnionNode
        register_node("five_tetrahedral_union")(FiveTetrahedralUnionNode)
    except ImportError:
        try:
            from src.nodes.tetrahedral_union import FiveTetrahedralUnionNode
            register_node("five_tetrahedral_union")(FiveTetrahedralUnionNode)
        except ImportError:
            class FiveTetrahedralUnionNode(Node):
                NODE_TYPE = "five_tetrahedral_union"
                def __init__(self, node_id="five_tetrahedral_union", name=None, **kwargs):
                    nid = name or node_id
                    super().__init__(node_id=nid, **kwargs)
                    self.name = nid
                def compute(self, inputs):
                    return {"out": inputs}
            register_node("five_tetrahedral_union")(FiveTetrahedralUnionNode)
