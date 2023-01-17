import unittest

from lang.himeko_meta_parser import Lark_StandAlone
from transformer.himeko_transformer import HypergraphRecursiveVisitor
from transformer.tensor_representation import HypergraphTensorTransformation


class TestBasicTransformation(unittest.TestCase):

    def read_node(self, path):
        # Transformer
        parser = Lark_StandAlone()
        # Read file
        with open(path) as f:
            tree = parser.parse(f.read())
        self.assertIsNotNone(tree, f"Unable to read tree from path {path}")
        return tree

    def test_node_hierarchy_edge_generation_hierarchy_evaluation_2(self):
        p = "../examples/simple/minimal_example_with_hierarchy_ref_edges_evaluation2.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        hyp_trans = HypergraphTensorTransformation()
        hyp_trans.encode(rvisitor.el_factory.root, 1e3)