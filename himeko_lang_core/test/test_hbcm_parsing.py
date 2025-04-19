import unittest

from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone
from himeko_lang.transformer.hypergraph.hypergraphmodel import HimekoHbcmTransformer


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
        print("\n--- START Test: test_basic_node_generation ---")
        p = "examples/simple/minimal_example.himeko"
        tree = self.read_node(p)
        rvisitor = HimekoHbcmTransformer()
        rvisitor.visit_topdown(tree)
        print("--- END Test: test_basic_node_generation ---")


    def test_basic_hierarchy(self):
        print("\n--- START Test: test_basic_node_generation ---")
        p = "examples/simple/minimal_example_basic_hierarchy.himeko"
        tree = self.read_node(p)
        rvisitor = HimekoHbcmTransformer()
        rvisitor.visit_topdown(tree)
        print("--- END Test: test_basic_node_generation ---")
