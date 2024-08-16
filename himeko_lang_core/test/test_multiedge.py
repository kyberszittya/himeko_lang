import os

from himeko.hbcm.elements.edge import HyperEdge, EnumRelationDirection
from test_ancestor_testcase import ERROR_MSG_UNABLE_TO_TRANSFORM

from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase

KINEMATIC_DESC_FOLDER = os.path.join("..", "examples", "simple", "multiedges")

TEST_CASE_MULTIEDGE_SIMPLE = (
    os.path.join(KINEMATIC_DESC_FOLDER, "multiedge_multidimensional_value.himeko"))


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
