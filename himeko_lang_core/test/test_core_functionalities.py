import unittest

from lang.graph.search_strategies import get_progenitor_chain
from lang.himeko_meta_parser import Lark_StandAlone
from lang.metaelements.himekoedge import HimekoEdge
from lang.metaelements.himekonode import HimekoNode
from lang.metaelements.himekovalue import HimekoValue
from transformer.himeko_transformer import HypergraphRecursiveVisitor


class TestBasicTransformation(unittest.TestCase):

    def read_node(self, path):

        # Transformer
        parser = Lark_StandAlone()
        # Read file
        with open(path) as f:
            tree = parser.parse(f.read())
        self.assertIsNotNone(tree, f"Unable to read tree from path {path}")
        return tree

    def test_basic_node_generation(self):
        p = "../examples/simple/minimal_example.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        self.assertEquals(len(rvisitor.el_factory.root._elements_by_uid), 0)

    def test_node_hierarchy_generation(self):
        p = "../examples/simple/minimal_example_basic_hierarchy.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        with open("test_node_hierarchy_generation_progenitytest") as f:
            progenity = f.readlines()[::-1]
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for n in rvisitor.el_factory._elements.values():
            self.assertEquals(progenity.pop().strip(), '<-'.join(get_progenitor_chain(n)))

    def test_node_hierarchy_edge_generation(self):
        p = "../examples/simple/minimal_example_with_edges.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        with open("test_node_edge_containment") as f:
            progenity = set(map(lambda x: x.strip(), f.readlines()[::-1]))
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 5)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            self.assertEquals(e.name, "e0")
            self.assertEquals(len(e._connections), 4)
            for x in e._connections.values():
                progenity.remove(x.target.name)
                self.assertEquals(f"{e.name}-{x.target.name}", x.name)

    def test_node_hierarchy_edge_generation_hierarchy(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            self.assertEquals(e.name, "e0")
            self.assertEquals(len(e._unknown_elements), 0)
            self.assertEquals(len(e._connections), 4)

    def test_node_hierarchy_edge_generation_hierarchy_evaluation(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges_evaluation.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            self.assertEquals(e.name, "e0")
            self.assertEquals(len(e._unknown_elements), 1)
            # Evaluate connections
            self.assertEquals(len(e._connections), 3)
            self.assertEquals(len(e._uneval_connections), 1)
            # Update unevaluated connections
            e.evaluate_unknown_references()
            self.assertEquals(len(e._connections), 4)
            self.assertEquals(len(e._uneval_connections), 0)

    def test_node_hierarchy_edge_generation_hierarchy_evaluation_2(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges_evaluation2.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            self.assertEquals(e.name, "e0")
            self.assertEquals(len(e._unknown_elements), 3)
            # Evaluate connections
            self.assertEquals(len(e._connections), 1)
            self.assertEquals(len(e._uneval_connections), 3)
            # Update unevaluated connections
            e.evaluate_unknown_references()
            self.assertEquals(len(e._connections), 4)
            self.assertEquals(len(e._uneval_connections), 0)

    def test_node_hierarchy_edge_generation_hierarchy_evaluation_unknown_references(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges_evaluation_unknown_references.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            self.assertEquals(e.name, "e0")
            self.assertEquals(len(e._unknown_elements), 3)
            # Evaluate connections
            self.assertEquals(len(e._connections), 0)
            self.assertEquals(len(e._uneval_connections), 4)
            # Update unevaluated connections
            e.evaluate_unknown_references()
            self.assertEquals(len(e._connections), 3)
            self.assertEquals(len(e._uneval_connections), 1)

    def test_node_hierarchy_edge_generation_with_edge_values(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges_with_values.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 4)
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            # Check values
            vals = []
            for c in e._connections.values():
                vals.extend(c.value)
            self.assertEquals(vals[0], 0.85)
            self.assertEquals(vals[1], 0.9)
            self.assertEquals(vals[2], -0.615)
            self.assertEquals(vals[3], 0.5)

    def test_multiple_edges(self):
        p = "../examples/simple/minimal_example_with_multiple_edges.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        n0 = next(rvisitor.el_factory.root.get_element_by_name("node_lev_0"))
        self.assertEquals(len(n0._elements_by_uid.values()), 9)
        self.assertEquals(len(list(filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()))), 3)
        self.assertEquals(len(list(filter(lambda x: isinstance(x, HimekoNode), rvisitor.el_factory._elements.values()))), 8)
        edges = {}
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            # Check values
            edges[e.name] = e
        self.assertIn("e0",edges)
        self.assertIn("e1",edges)
        self.assertIn("e2",edges)
        # Check connections
        self.assertEquals(len(edges["e0"]._connections.values()), 4)
        self.assertEquals(len(edges["e1"]._connections.values()), 2)
        self.assertEquals(len(edges["e2"]._connections.values()), 2)

    def test_node_fields(self):
        p = "../examples/simple/minimal_example_fields.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        values = {}
        for v in filter(lambda x: isinstance(x, HimekoValue), rvisitor.el_factory._elements.values()):
            values[v.name] = v
        self.assertEquals(values["val0"].value, 56)
        self.assertIsInstance(values["val0"].value, int)
        self.assertTrue(values["val0"].is_assigned, 56.891)
        self.assertEquals(values["val1"].value, "vakond")
        self.assertTrue(values["val1"].is_assigned)
        self.assertEquals(values["val2"].value, 56.891)
        self.assertTrue(values["val2"].is_assigned)
        self.assertIsInstance(values["val2"].value, float)
        self.assertFalse(values["val_undef"].is_assigned)
        self.assertEquals(values["val3"].value, "3444.4623")
        self.assertEquals(values["pi"].value, "3.14156")
        self.assertTrue("val_float" in values)

