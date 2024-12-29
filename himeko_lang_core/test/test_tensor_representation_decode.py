import numpy as np

from himeko.common.clock import NullClock
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.graph.prufer_sequence import reconstruct_naive_prufer
from himeko.hbcm.mapping.meta.tensor_mapping import HypergraphTensor
from himeko.hbcm.mapping.tensor_channel import DefaultTensorChannel
from himeko.hbcm.mapping.tensor_mapping import BijectiveCliqueExpansionTransformation, StarExpansionTransformation
from himeko.hbcm.transformations.transmission import copy_node_list
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase


class TestBasicTransformationEncoding(TestAncestorTestCase):

    def test_directed3_nodes_1_clique_expansion(self):
        p = "../examples/simple/tensor/directed_3_nodes_1.himeko"
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = BijectiveCliqueExpansionTransformation()
        channel = DefaultTensorChannel(tr)
        tensor, n, n_e, pr_code, perm_seq = channel.transmit(root_el)
        self.assertEqual(n, 3)
        self.assertEqual(n_e, 3)
        x_e1 = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [0, 0, 0]])
        x_e2 = np.array([[0, 0, 0],
                         [0, 0, 0],
                         [1, 0, 0]])
        x_e3 = np.array([[0, 0, 0],
                         [0, 0, 1],
                         [0, 0, 0]])
        tx = np.array([x_e1,x_e2,x_e3])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))
        # Copy node map
        copy_node, list_copy_node, copy_node_map = copy_node_list(perm_seq)
        # Check sequence
        self.assertEqual(len(perm_seq), 7)
        self.assertEqual(len(pr_code), 6)
        self.assertEqual([x.name for x in perm_seq],
                         ['node1', 'node2', 'node3', 'e1', 'e2', 'e3', 'graph'])
        # Check if Prüfer sequence contain only graph as parent
        for x in pr_code:
            self.assertEqual(x, root_el)
        # Decode hypergraph from tensor
        new_root: HyperVertex = reconstruct_naive_prufer([x.guid for x in pr_code],
                                                         [x.guid for x in perm_seq],
                                                         copy_node_map)
        self.assertEqual(new_root.name, "graph")
        self.assertEqual([x.name for x in new_root.permutation_sequence],
                         [x.name for x in root_el.permutation_sequence])
        self.assertEqual([x.name for x in new_root.edge_order],
                         [x.name for x in root_el.edge_order])
        # Check if new edges do not contain any relations
        for e in new_root.edge_order:
            e: HyperEdge
            self.assertEqual(len(list(e.out_relations())), 0)
            self.assertEqual(len(list(e.in_relations())), 0)
            # Check if edges have parents anyway
            self.assertIsNotNone(e.parent)
        # Decode
        msg = HypergraphTensor(tensor, n, n_e,
                               new_root.permutation_sequence,
                               new_root.prufer_code,
                               new_root.edge_order)
        channel.receive(msg)
        # Encode new root once again
        new_tensor, new_n, new_e, new_pr_code, new_perm_seq = channel.transmit(new_root)
        # Check if dimensions and codes are the same by values
        self.assertEqual(n, new_n)
        self.assertEqual(n_e, new_e)
        self.assertEqual([x.guid for x in pr_code], [x.guid for x in new_pr_code])
        self.assertEqual([x.guid for x in perm_seq], [x.guid for x in new_perm_seq])

        # Check if the tensor is the same
        self.assertTrue(np.all(tensor == new_tensor))

    def test_directed3_nodes_1_star_expansion(self):
        p = "../examples/simple/tensor/directed_3_nodes_1.himeko"
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root_el = hyv[-1]
        self.assertEqual(root_el.name, "graph")
        tr = StarExpansionTransformation()
        channel = DefaultTensorChannel(tr)
        tensor, n, n_e, pr_code, perm_seq = channel.transmit(root_el)
        self.assertEqual(n, 6)
        self.assertEqual(n_e, 3)
        x_e1 = np.array(
            [[0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 1., 0., 0.],
             [0., 0., 0., 0., 0., 0.],
             [1., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.]]
        )
        x_e2 = np.array(
            [[0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 1., 0.],
             [0., 0., 0., 0., 0., 0.],
             [1., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.]]
        )
        x_e3 = np.array(
            [[0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 1.],
             [0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.],
             [0., 0., 0., 0., 0., 0.],
             [0., 0., 1., 0., 0., 0.]]
        )
        tx = np.array([x_e1,x_e2,x_e3])
        self.assertTrue(np.all(tx == tensor[:, :n, :n]))
        # Copy node map
        copy_node, list_copy_node, copy_node_map = copy_node_list(perm_seq)
        # Check sequence
        self.assertEqual(len(perm_seq), 7)
        self.assertEqual(len(pr_code), 6)
        self.assertEqual([x.name for x in perm_seq],
                         ['node1', 'node2', 'node3', 'e1', 'e2', 'e3', 'graph'])
        # Check if Prüfer sequence contain only graph as parent
        for x in pr_code:
            self.assertEqual(x, root_el)
        # Decode hypergraph from tensor
        new_root: HyperVertex = reconstruct_naive_prufer([x.guid for x in pr_code],
                                                         [x.guid for x in perm_seq],
                                                         copy_node_map)
        self.assertEqual(new_root.name, "graph")
        self.assertEqual([x.name for x in new_root.permutation_sequence],
                         [x.name for x in root_el.permutation_sequence])
        self.assertEqual([x.name for x in new_root.edge_order],
                         [x.name for x in root_el.edge_order])
        # Check if new edges do not contain any relations
        for e in new_root.edge_order:
            e: HyperEdge
            self.assertEqual(len(list(e.out_relations())), 0)
            self.assertEqual(len(list(e.in_relations())), 0)
            # Check if edges have parents anyway
            self.assertIsNotNone(e.parent)
        # Decode
        msg = HypergraphTensor(tensor, n, n_e,
                               new_root.permutation_sequence,
                               new_root.prufer_code,
                               new_root.edge_order)
        channel.receive(msg)
        # Encode new root once again
        new_tensor, new_n, new_e, new_pr_code, new_perm_seq = channel.transmit(new_root)
        # Check if dimensions and codes are the same by values
        self.assertEqual(n, new_n)
        self.assertEqual(n_e, new_e)
        self.assertEqual([x.guid for x in pr_code], [x.guid for x in new_pr_code])
        self.assertEqual([x.guid for x in perm_seq], [x.guid for x in new_perm_seq])
        # Check if the tensor is the same
        self.assertTrue(np.all(tensor == new_tensor))


