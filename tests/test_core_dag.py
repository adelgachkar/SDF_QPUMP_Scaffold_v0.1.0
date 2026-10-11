import unittest
from qpump.core import Graph
from qpump.nodes.base import Node
class AddNode(Node):
    type_name="add_test"
    def compute(self, inputs): return {"out": inputs.get("x",0)+inputs.get("y",0)}
class CoreDagTests(unittest.TestCase):
    def test_routing_and_deterministic_execution(self):
        graph=Graph(); graph.add_node(AddNode("a")); graph.add_node(AddNode("b")); graph.connect("a","out","b","x")
        out=graph.run({"a":{"x":2,"y":3},"b":{"y":4}})
        self.assertEqual(out["a"]["out"],5); self.assertEqual(out["b"]["out"],9)
        self.assertEqual(graph._order(),["a","b"])
    def test_cycle_rejected(self):
        graph=Graph(); graph.add_node(AddNode("a")); graph.add_node(AddNode("b")); graph.connect("a","out","b","x"); graph.connect("b","out","a","x")
        with self.assertRaisesRegex(ValueError,"cycle"): graph.run()
    def test_duplicate_and_missing_nodes(self):
        graph=Graph(); graph.add_node(AddNode("a"))
        with self.assertRaisesRegex(ValueError,"duplicate"): graph.add_node(AddNode("a"))
        with self.assertRaises(KeyError): graph.connect("a","out","missing","x")
    def test_missing_output_port_is_reported(self):
        graph=Graph(); graph.add_node(AddNode("a")); graph.add_node(AddNode("b")); graph.connect("a","absent","b","x")
        with self.assertRaisesRegex(KeyError,"missing output"): graph.run()
if __name__=="__main__": unittest.main()
