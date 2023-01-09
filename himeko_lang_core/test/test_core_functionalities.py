import unittest

from lang.graph.search_strategies import get_progenitor_chain
from lang.himeko_meta_parser import Lark_StandAlone
from lang.metaelements.himekoedge import HimekoEdge
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

    def test_node_hierarchy_generation(self):
        p = "../examples/simple/minimal_example_basic_hierarchy.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        with open("test_node_hierarchy_generation_progenitytest") as f:
            progenity = f.readlines()[::-1]
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        for n in rvisitor.el_factory._elements.values():
            self.assertEquals(progenity.pop().strip(), '<-'.join(get_progenitor_chain(n)))

    def test_node_hierarchy_edge_generation(self):
        p = "../examples/simple/minimal_example_with_edges.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        with open("test_node_hierarchy_generation_progenitytest") as f:
            progenity = f.readlines()[::-1]
        self.assertEquals(rvisitor.el_factory.root.name, "context")
        for e in filter(lambda x: isinstance(x, HimekoEdge), rvisitor.el_factory._elements.values()):
            for x in e._connections.values():
                print(x.name, x.target.name)

