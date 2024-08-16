import os

from himeko.hbcm.elements.edge import HyperEdge, EnumRelationDirection
from test_ancestor_testcase import ERROR_MSG_UNABLE_TO_TRANSFORM

from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase

KINEMATIC_DESC_FOLDER = os.path.join("..", "examples", "simple", "multiedges")

TEST_CASE_MULTIEDGE_SIMPLE = (
    os.path.join(KINEMATIC_DESC_FOLDER, "multiedge_multidimensional_value.himeko"))

TEST_CASE_MULTIEDGE_EMBEDDED_SIMPLE = (
    os.path.join(KINEMATIC_DESC_FOLDER, "multiedge_embedded_edge.himeko")
)

TEST_CASE_MULTIEDGE_SIGNAGTURE_VALUES = (
    os.path.join(KINEMATIC_DESC_FOLDER, "multiedge_signature_values.himeko")
)


class TestBasicKinematicsAstParsing(TestAncestorTestCase):

    def test_load_multi_edge(self):
        root = self.read_node(TEST_CASE_MULTIEDGE_SIMPLE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "context")
        # Edge
        self.assertIsNotNone(root["e"])
        e: HyperEdge = root["e"]
        self.assertIsInstance(e, HyperEdge)
        out_rel = list(e.out_relations())
        self.assertEqual(len(out_rel), 2)
        # Get node0
        node0 = root["node_lev_0"]["node0"]["node0"]
        node1 = root["node_lev_0"]["node1"]
        node2 = root["node_lev_0"]["node2"]
        # Out relation 1
        self.assertEqual(len(out_rel[0].value), 3)
        self.assertEqual(out_rel[0].value[0], [1.0, 19.3, 1.2])
        self.assertEqual(out_rel[0].value[1], [2.1, 3.2])
        self.assertEqual(out_rel[0].value[2], [78.1, 7.3, 2.19])
        self.assertEqual(out_rel[0].target.name, "node0")
        self.assertEqual(out_rel[0].target, node0)
        self.assertEqual(out_rel[0].direction, EnumRelationDirection.OUT)
        # Incoming relation 1
        in_rel = list(e.in_relations())
        self.assertEqual(len(in_rel), 1)
        self.assertEqual(in_rel[0].value[0], [1.2, 1.5])
        self.assertEqual(in_rel[0].value[1], [5.6, 3.4])
        self.assertEqual(in_rel[0].value[2], [1.0, 6.7])
        self.assertEqual(in_rel[0].target.name, "node1")
        self.assertEqual(in_rel[0].target, node1)
        self.assertEqual(in_rel[0].direction, EnumRelationDirection.IN)
        # Out relation 2
        self.assertEqual(len(out_rel[1].value), 3)
        self.assertEqual(out_rel[1].value, [0.5, 0.7, 0.9])
        self.assertEqual(out_rel[1].target.name, "node2")
        self.assertEqual(out_rel[1].target, node2)

    def test_load_multi_edge_embedded(self):
        root = self.read_node(TEST_CASE_MULTIEDGE_EMBEDDED_SIMPLE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "context")
        # Edge
        self.assertIsNotNone(root["e"])
        e: HyperEdge = root["e"]
        self.assertIsInstance(e, HyperEdge)
        # Relations
        out_rel = list(e.out_relations())
        self.assertEqual(len(out_rel), 1)
        in_rel = list(e.in_relations())
        self.assertEqual(len(in_rel), 1)
        # Get node0
        node0 = root["node_lev_0"]["node0"]["node0"]
        node1 = root["node_lev_0"]["node1"]
        node2 = root["node_lev_0"]["node2"]
        node3 = root["node_lev_0"]["node3"]
        # Out relation 1
        self.assertEqual(len(out_rel[0].value), 3)
        self.assertEqual(out_rel[0].value[0], [1.0, 19.3, 1.2])
        self.assertEqual(out_rel[0].value[1], [2.1, 3.2])
        self.assertEqual(out_rel[0].value[2], [78.1, 7.3, 2.19])
        self.assertEqual(out_rel[0].target.name, "node0")
        self.assertEqual(out_rel[0].target, node0)
        self.assertEqual(out_rel[0].direction, EnumRelationDirection.OUT)
        # Incoming relation 1
        self.assertEqual(len(in_rel[0].value), 3)
        self.assertEqual(in_rel[0].value[0], [1.2, 1.5])
        self.assertEqual(in_rel[0].value[1], [5.6, 3.4])
        self.assertEqual(in_rel[0].value[2], [1.0, 6.7])
        self.assertEqual(in_rel[0].target.name, "node1")
        self.assertEqual(in_rel[0].target, node1)
        self.assertEqual(in_rel[0].direction, EnumRelationDirection.IN)
        # Check embedded edges (sub edges)
        sub_edges = list(e.sub_edges())
        self.assertEqual(len(sub_edges), 2)
        # Sub edge 1
        sub_edge = sub_edges[0]
        self.assertEqual(sub_edge.name, "e1")
        # Relations
        out_rel = list(sub_edge.out_relations())
        self.assertEqual(len(out_rel), 1)
        in_rel = list(sub_edge.in_relations())
        self.assertEqual(len(in_rel), 1)
        # In relation 1
        self.assertEqual(len(in_rel[0].value), 3)
        self.assertEqual(in_rel[0].value[0], [1.2, 1.5])
        self.assertEqual(in_rel[0].value[1], [5.6, 3.4])
        self.assertEqual(in_rel[0].value[2], [1.0, 6.7])
        self.assertEqual(in_rel[0].target.name, "node1")
        self.assertEqual(in_rel[0].target, node1)
        # Out relation 1
        self.assertEqual(len(out_rel[0].value), 3)
        self.assertEqual(out_rel[0].value, [0.5, 0.7, 0.9])
        self.assertEqual(out_rel[0].target.name, "node2")
        self.assertEqual(out_rel[0].target, node2)
        # Sub edge 2
        sub_edge = sub_edges[1]
        self.assertEqual(sub_edge.name, "e2")
        # Relations
        out_rel = list(sub_edge.out_relations())
        self.assertEqual(len(out_rel), 1)
        in_rel = list(sub_edge.in_relations())
        self.assertEqual(len(in_rel), 1)
        # In relation 1
        self.assertEqual(len(in_rel[0].value), 3)
        self.assertEqual(in_rel[0].value[0], [1.76, 9.3])
        self.assertEqual(in_rel[0].value[1], [5.1, 8.4])
        self.assertEqual(in_rel[0].value[2], [4.9, 6.8])
        self.assertEqual(in_rel[0].target.name, "node2")
        self.assertEqual(in_rel[0].target, node2)
        # Out relation 1
        self.assertEqual(len(out_rel[0].value), 3)
        self.assertEqual(out_rel[0].value, [0.52, 0.94, 0.99])
        self.assertEqual(out_rel[0].target.name, "node3")
        self.assertEqual(out_rel[0].target, node3)

    def test_load_multidiensional_signature(self):
        root = self.read_node(TEST_CASE_MULTIEDGE_SIGNAGTURE_VALUES)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "context")
        # Edge
        self.assertIsNotNone(root["e"])
        e: HyperEdge = root["e"]
        self.assertIsInstance(e, HyperEdge)
        # Relations
        out_rel = list(e.out_relations())
        self.assertEqual(len(out_rel), 2)
        in_rel = list(e.in_relations())
        self.assertEqual(len(in_rel), 1)
        # Get node0
        node0 = root["node_lev_0"]["node0"]["node0"]
        node1 = root["node_lev_0"]["node1"]
        node2 = root["node_lev_0"]["node2"]
        # Out relation 1
        self.assertEqual(len(out_rel[0].value), 3)
        self.assertEqual(out_rel[0].value[0], [1.0, 19.3, 1.2])
        print("Signature value rel0: ", out_rel[0].value)
        self.assertEqual(out_rel[0].value, [[1.0, 19.3, 1.2], [2.1, 3.2, [45.7, 23.4]], [[56.7, 67.8], 56.8, 24.2]])
        self.assertEqual(out_rel[0].target.name, "node0")
        self.assertEqual(out_rel[0].target, node0)
        self.assertEqual(out_rel[0].direction, EnumRelationDirection.OUT)
        # Incoming relation 1
        self.assertEqual(len(in_rel[0].value), 4)
        print("Signature value rel1: ", in_rel[0].value)
        self.assertEqual(in_rel[0].value, [[1.2, [3.2, 4.8], 1.5], [5.6, 3.4, [7.2, 12.54]], [1.0, 6.7], [1.3, 7.8, 1.2]])
        self.assertEqual(in_rel[0].target.name, "node1")
        self.assertEqual(in_rel[0].target, node1)
        self.assertEqual(in_rel[0].direction, EnumRelationDirection.IN)
        # Out relation 2
        self.assertEqual(len(out_rel[1].value), 3)
        self.assertEqual(out_rel[1].value, [0.5, 0.7, 0.9])
        self.assertEqual(out_rel[1].target.name, "node2")
        self.assertEqual(out_rel[1].target, node2)
        print("Signature value rel2: ", out_rel[1].value)
        self.assertEqual(out_rel[1].direction, EnumRelationDirection.OUT)
