import os


from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from test_ancestor_testcase import ERROR_MSG_UNABLE_TO_TRANSFORM

from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase

CAMERA_DESC_FOLDER = os.path.join("..", "examples", "kinematics")

TEST_CASE_ROBOT_ARM_PARSING = (
    os.path.join(CAMERA_DESC_FOLDER, "anthropomorphic_arm.himeko"))


class TestBasicKinematicsAstParsing(TestAncestorTestCase):

    def test_load_arm_desc(self):
        root = self.read_node(TEST_CASE_ROBOT_ARM_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "robot")
        robot_arm = next(root.get_children(lambda x: x.name == "robot_arm", 1))
        print(robot_arm)
        self.assertIsNotNone(robot_arm, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(robot_arm.name, "robot_arm")
        nodes = list(robot_arm.get_children_nodes(lambda x: True, 1))
        for n in nodes:
            print("Link: ", n.name)
        node_names_set = set([x.name for x in nodes])
        # Check nodes
        self.assertEqual(len(node_names_set), 7)
        self.assertIn("base_link", node_names_set)
        # Link 0
        self.assertIn("link_0", node_names_set)
        link_0 = next(robot_arm.get_children(lambda x: x.name == "link_0", 1))
        self.assertIsInstance(link_0, HyperVertex)
        self.assertEqual(link_0.name, "link_0")
        self.assertEqual(link_0.template.name, "link")
        self.assertEqual(link_0["mass"].value, 5.0)
        cylinder_link = link_0["link_geometry"]["geometry"]
        self.assertIsInstance(cylinder_link, HypergraphAttribute)
        self.assertEqual(cylinder_link.value.name, "cylinder")
        # Link 1
        self.assertIn("link_1", node_names_set)
        link_1 = next(robot_arm.get_children(lambda x: x.name == "link_1", 1))
        cylinder_link_1 = link_1["link_geometry"]["geometry"]
        self.assertIsInstance(cylinder_link_1, HypergraphAttribute)
        self.assertEqual(cylinder_link_1.value.name, "cylinder")
        self.assertEqual(cylinder_link.value, cylinder_link_1.value)
        # Link 2
        self.assertIn("link_2", node_names_set)
        link_2 = next(robot_arm.get_children(lambda x: x.name == "link_2", 1))
        cylinder_link_2 = link_2["link_geometry"]["geometry"]
        self.assertEqual(link_2["link_geometry"]["dimension"].value, [0.075, 0.25])
        self.assertIsInstance(cylinder_link_2, HypergraphAttribute)
        self.assertEqual(cylinder_link_2.value.name, "cylinder")
        self.assertEqual(cylinder_link.value, cylinder_link_2.value)
        self.assertEqual(link_2["visual"].value, link_2["link_geometry"])
        self.assertEqual(link_2["collision"].value, link_2["link_geometry"])
        # Link 3
        self.assertIn("link_3", node_names_set)
        self.assertIn("link_4", node_names_set)
        self.assertIn("tool", node_names_set)

        print(robot_arm.name)
        # Edges
        edges = list(robot_arm.get_children(lambda x: isinstance(x, HyperEdge), 1))
        edge_names = set([x.name for x in edges])
        self.assertEqual(len(edge_names), 6)
        self.assertIn("j0", edge_names)
        self.assertIn("j1", edge_names)
        self.assertIn("j2", edge_names)
        self.assertIn("j3", edge_names)
        self.assertIn("j4", edge_names)
        self.assertIn("jtool", edge_names)
        # Check edge connections
        j0 = next(robot_arm.get_children(lambda x: x.name == "j0", 1))
        self.assertIsInstance(j0, HyperEdge)
        self.assertEqual(j0.cnt_in_relations, 1)
        j0_out_relations = list(j0.out_relations())
        out_vertices_names = set([x.target.name for x in j0_out_relations])
        self.assertIn("link_0", out_vertices_names)
        self.assertIn("AXIS_Z", out_vertices_names)
        self.assertIn("joint_rev_limit", out_vertices_names)
        # Check incoming relation (base_link mor particularly) of J0
        j0_in_relations = list(j0.in_relations())
        in_vertices_names = set([x.target.name for x in j0_in_relations])
        self.assertIn("base_link", in_vertices_names)
