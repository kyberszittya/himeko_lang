from himeko.common.clock import NullClock
from himeko.hbcm.mapping.tensor_mapping import BijectiveCliqueExpansionTransformation, StarExpansionTransformation
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from .test_ancestor_testcase import TestAncestorTestCase

import numpy as np
import os

EXAMPLES_FOLDER = os.path.join("examples")
SIMPLE_EXAMPLES_FOLDER = os.path.join(EXAMPLES_FOLDER, "simple")


class TestBasicTransformationEncoding(TestAncestorTestCase):

    def test_node_hierarchy_edge_generation_hierarchy_evaluation_2(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "minimal_example_with_hierarchy_ref_edges_evaluation2.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "context")
        # Tensor mapping


    def test_directed3_nodes_1(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "tensor/directed_3_nodes_1.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 3)
        self.assertEqual(e, 3)
        x_e1 = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 0]])
        x_e2 = np.array([[0, 0, 0], [0, 0, 0], [1, 0, 0]])
        x_e3 = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])
        tx = np.array([x_e1,x_e2,x_e3])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))

    def test_directed3_nodes_1_star_expansion(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "tensor/directed_3_nodes_1.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = StarExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 6)
        self.assertEqual(e, 3)
        # Star expansion tensor
        print(tensor)
        x_e1 = np.array(
            [[0, 0, 0, 0, 0, 0],
             [0, 0, 0, 1, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
        )
        x_e2 = np.array(
            [[0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0],
             [1, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0]]
        )
        x_e3 = np.array(
            [[0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0],
             [0, 0, 1, 0, 0, 0]]
        )
        tx = np.array([x_e1,x_e2,x_e3])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))


    def test_directed3_nodes_2(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "tensor/directed_3_nodes_2.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 3)
        self.assertEqual(e, 3)
        x_e1 = np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
        x_e2 = np.array([[0, 0, 0], [0, 0, 0], [1, 0, 0]])
        x_e3 = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 0]])
        tx = np.array([x_e1,x_e2,x_e3])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))

    def test_directed4_nodes_1(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "tensor/directed_4_nodes_1.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 4)
        self.assertEqual(e, 5)
        x2_e1 = np.array([[0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [1, 0, 0, 0]])
        x2_e2 = np.array([[0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [1, 0, 0, 0],
                          [0, 0, 0, 0]])
        x2_e3 = np.array([[0, 0, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])
        x2_e4 = np.array([[0, 1, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 0]])
        x2_e5 = np.array([[0, 0, 0, 0],
                          [0, 0, 0, 0],
                          [0, 0, 0, 1],
                          [0, 0, 0, 0]])
        tx = np.array([x2_e1,x2_e2,x2_e3, x2_e4, x2_e5])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))

    def test_directed_factor_graph1(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "tensor/factor_directed_graph_1.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 5)
        self.assertEqual(e, 2)
        print(tensor)
        x2_e1 = np.array([[0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0],
                          [1, 1, 0, 0, 0],
                          [1, 1, 0, 0, 0]])
        x2_e2 = np.array([[0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 1],
                          [0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0]])
        tx = np.array([x2_e1,x2_e2])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))

    def test_directed_fano_graph(self):
        p = os.path.join(SIMPLE_EXAMPLES_FOLDER, "base/fano_graph.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "fano")
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        self.assertEqual(n, 7)
        self.assertEqual(e, 7)
        self.assertTrue(np.all(np.sum(tensor[:, :n, :n], axis=0) - np.eye(7)))
        # Ensure aggregated tensor is symmetric
        aggregate_tensor = np.sum(tensor, axis=0)
        self.assertTrue(np.all(aggregate_tensor == aggregate_tensor.T))
        # Ensure aggregated tensor is equal to a full matrix with ones besides the diagonal
        self.assertTrue(np.all(aggregate_tensor == np.ones((7, 7)) - np.eye(7)))

    def test_fuzzy_signature(self):
        p = os.path.join(EXAMPLES_FOLDER, "fuzzy/fuzzy_signature_example.himeko")
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        tr = BijectiveCliqueExpansionTransformation()
        tensor, n, e = tr.encode(root_el)
        x2_e1 = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.4, 0, 0, 0], # 1
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 5
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 10
                          [0, 0.9, 0.4, 0.2, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0]

        ])
        x2_e2 = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 1
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.9, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 5
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 10
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0.9, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0]
        ])
        x2_e3 = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 1
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.4, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 5
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 10
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0.4, 0.5, 0.7, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0]
                          ])
        x2_e4 = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 1
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 5
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0], # 10
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0, 0, 0, 0.2, 0.1, 0.0, 0, 0, 0]
                          ])
        tx = np.array([x2_e1,x2_e2,x2_e3, x2_e4])
        # Visualize the tensor with imshow
        from matplotlib import pyplot as plt
        # Aggregate tensor
        aggregate_tensor = np.sum(tx, axis=0)
        # Checkboard pattern for visualization
        checkboard = np.zeros((14, 14))
        for i in range(14):
            for j in range(14):
                if (i + j) % 2 == 0:
                    checkboard[i, j] = 1
        # SHow the checkboard pattern in the background
        plt.imshow(checkboard, cmap='gray', interpolation='nearest', alpha=0.2)
        # Use imshow to visualize the tensor with fancy colors, no viridis, no axes, not plasma
        # Let be the zero value white, and the rest of the values are colored
        plt.imshow(aggregate_tensor, cmap='coolwarm', interpolation='nearest', alpha=0.9)
        plt.colorbar()
        # Remove axes
        plt.axis('off')
        plt.grid()
        plt.show()

