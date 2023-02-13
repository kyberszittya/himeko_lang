import unittest

from lang.himeko_meta_parser import Lark_StandAlone
from transformer.himeko_transformer import HypergraphRecursiveVisitor
from transformer.tensor_representation import HypergraphTensorTransformation

import numpy as np


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
        root_el = rvisitor.el_factory.root
        root_el.evaluate_unknown_references()
        hyp_trans = HypergraphTensorTransformation()
        _tensor = hyp_trans.encode(root_el, 1e3)
        print(_tensor)

    def test_directed3_nodes_1(self):
        p = "../examples/simple/tensor/directed_3_nodes_1.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        root_el = rvisitor.el_factory.root
        root_el.evaluate_unknown_references()
        hyp_trans = HypergraphTensorTransformation()
        _tensor = hyp_trans.encode(root_el, 1e3)
        x_e1 = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]])
        x_e2 = np.array([[0, 0, -1], [0, 0, 0], [1, 0, 0]])
        x_e3 = np.array([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        Tx = np.array([x_e1,x_e2,x_e3])
        assert(np.all(Tx == _tensor))

    def test_directed3_nodes_2(self):
        p = "../examples/simple/tensor/directed_3_nodes_2.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        root_el = rvisitor.el_factory.root
        root_el.evaluate_unknown_references()
        hyp_trans = HypergraphTensorTransformation()
        _tensor = hyp_trans.encode(root_el, 1e3)
        x_e1 = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]])
        x_e2 = np.array([[0, 0, -1], [0, 0, 0], [1, 0, 0]])
        x_e3 = np.array([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        Tx = np.array([x_e1,x_e2,x_e3])
        assert(np.all(Tx == _tensor))

    def test_directed4_nodes_1(self):
        p = "../examples/simple/tensor/directed_4_nodes_1.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        root_el = rvisitor.el_factory.root
        root_el.evaluate_unknown_references()
        hyp_trans = HypergraphTensorTransformation()
        _tensor = hyp_trans.encode(root_el, 1e3)
        x2_e1 = np.array([[0, 1, 0, 0],
                          [-1, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])
        x2_e2 = np.array([[0, 0, 0, 0],
                          [0, 0, 1, 0],
                          [0, -1, 0, 0],
                          [0, 0, 0, 0]])
        x2_e3 = np.array([[0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 1],
                          [0, 0, -1, 0]])
        x2_e4 = np.array([[0, 0, 0, -1],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [1, 0, 0, 0]])
        x2_e5 = np.array([[0, 0, -1, 0],
                          [0, 0, 0, 0],
                          [1, 0, 0, 0],
                          [0, 0, 0, 0]])
        Tx = np.array([x2_e1,x2_e2,x2_e3, x2_e4, x2_e5])
        assert(np.all(Tx == _tensor))

    def test_directed_factor_graph1(self):
        p = "../examples/simple/tensor/factor_directed_graph_1.himeko"
        tree = self.read_node(p)
        rvisitor = HypergraphRecursiveVisitor()
        rvisitor.visit_topdown(tree)
        root_el = rvisitor.el_factory.root
        root_el.evaluate_unknown_references()
        hyp_trans = HypergraphTensorTransformation()
        _tensor = hyp_trans.encode(root_el, 1e3)
        x2_e1 = np.array([[0, 0, 0, -1, -1],
                          [0, 0, 0, -1, -1],
                          [0, 0, 0, 0, 0],
                          [1, 1, 0, 0, 0],
                          [1, 1, 0, 0, 0]])
        x2_e2 = np.array([[0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 0],
                          [0, -1, -1, 0, 0]])
        Tx = np.array([x2_e1,x2_e2])
        assert(np.all(Tx == _tensor))