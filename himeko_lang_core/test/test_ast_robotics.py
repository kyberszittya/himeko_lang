import os
import logging

from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.hbcm.queries.composition import QueryIsStereotypeOperation
from himeko.hbcm.visualization.graphviz import create_dot_graph, visualize_dot_graph
from himeko.transformations.ros.urdf import TransformationUrdf
from himeko.transformations.ros.robot_queries import FactoryRobotQueryElements
from himeko_lang.lang.engine.load_desc import HypergraphLoader
from test_ancestor_testcase import ERROR_MSG_UNABLE_TO_TRANSFORM

from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase

KINEMATIC_DESC_FOLDER = os.path.join("..", "examples", "kinematics")

TEST_CASE_ROBOT_ARM_PARSING = (
    os.path.join(KINEMATIC_DESC_FOLDER, "robotics", "anthropomorphic_arm.himeko"))

TEST_CASE_META_KINEMATICS_PARSING = (
    os.path.join(KINEMATIC_DESC_FOLDER, "meta_kinematics.himeko"))

TEST_CASE_META_KINEMATICS_IMPORT_PARSING = (
    os.path.join(KINEMATIC_DESC_FOLDER, "robotics", "anthropomorphic_arm_import.himeko")
)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import unittest


class TestBasicKinematicsAstParsing(TestAncestorTestCase):

    def test_load_arm_desc(self):
        logger.info("START: test_load_arm_desc")
        #
        root = self.read_node(TEST_CASE_ROBOT_ARM_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "robot")
        robot_arm = next(root.get_children(lambda x: x.name == "robot_arm", 1))
        logger.info(robot_arm)
        self.assertIsNotNone(robot_arm, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(robot_arm.name, "robot_arm")
        nodes = list(robot_arm.get_children_nodes(lambda x: True, 1))
        for n in nodes:
            logger.info("Link: {}".format(n.name))
        node_names_set = set([x.name for x in nodes])
        # Check nodes
        self.assertEqual(len(node_names_set), 7)
        self.assertIn("base_link", node_names_set)
        # Link 0
        self.assertIn("link_0", node_names_set)
        link_0 = next(robot_arm.get_children(lambda x: x.name == "link_0", 1))
        self.assertIsInstance(link_0, HyperVertex)
        self.assertEqual(link_0.name, "link_0")
        self.assertEqual(link_0.stereotype[0].name, "link")
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

        logger.info(robot_arm.name)
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
        # Logger
        logger.info("END: test_load_arm_desc")

    def test_load_meta_desc(self):
        logger.info("START: test_load_meta_desc")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertEqual(root.name, "kinematics")
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        # Check units
        units = root["units"]
        self.assertIsInstance(units, HyperVertex)
        self.assertEqual(units.name, "units")
        self.assertIsInstance(units["length"], HypergraphAttribute)
        self.assertEqual(units["length"].value, "m")
        self.assertEqual(units["angle"].value, "degree")
        self.assertEqual(units["time"].value, "s")
        self.assertEqual(units["mass"].value, "kg")
        # Check elements
        elements = root["elements"]
        self.assertIsInstance(elements, HyperVertex)
        # Check link and joint
        self.assertIsInstance(elements["link"], HyperVertex)
        link = elements["link"]
        self.assertIsInstance(link, HyperVertex)
        self.assertEqual(link.name, "link")
        # Check meta element stereotype
        self.assertEqual(link.stereotype[0].name, "meta_element")
        self.assertIsInstance(elements["joint"], HyperEdge)
        # Check rev joint
        rev_joint = root["rev_joint"]
        self.assertIsInstance(rev_joint, HyperEdge)

        # Check if rev joint has joint as stereotype
        self.assertEqual(rev_joint.stereotype[0].name, "joint")
        # Check if rev joint is connected to limit
        rev_joint_out_relations = list(rev_joint.out_relations())
        out_vertices_names = set([x.target.name for x in rev_joint_out_relations])
        # Check geometry vertex contents
        geometry = root["geometry"]
        # Sphere, cylinder, box should be present
        self.assertIsInstance(geometry, HyperVertex)
        self.assertEqual(geometry.name, "geometry")
        self.assertIsInstance(geometry["sphere"], HyperVertex)
        self.assertIsInstance(geometry["cylinder"], HyperVertex)
        self.assertIsInstance(geometry["box"], HyperVertex)
        # Check axes
        axes = root["axes"]
        self.assertIsInstance(axes, HyperVertex)
        self.assertEqual(axes.name, "axes")
        self.assertIsInstance(axes["AXIS_X"], HyperVertex)
        self.assertEqual(axes["AXIS_X"]["ax"].value, [1, 0, 0])
        self.assertIsInstance(axes["AXIS_Y"], HyperVertex)
        self.assertEqual(axes["AXIS_Y"]["ax"].value, [0, 1, 0])
        self.assertIsInstance(axes["AXIS_Z"], HyperVertex)
        self.assertEqual(axes["AXIS_Z"]["ax"].value, [0, 0, 1])
        #
        logger.info("END: test_load_meta_desc")

    def test_load_arm_import_desc(self):
        logger.info("START: test_load_arm_import_desc")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_IMPORT_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root, KINEMATIC_DESC_FOLDER)
        root = hyv[-1]
        self.assertEqual(root.name, "robot")
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        robot = root
        # Base link
        base_link = robot["base_link"]
        self.assertIsInstance(base_link, HyperVertex)
        self.assertEqual(base_link.name, "base_link")
        self.assertEqual(base_link["mass"].value, 25.0)
        self.assertEqual(base_link.stereotype[0].name, "link")
        self.assertIn("link", base_link.stereotype.nameset)
        #
        logger.info("END: test_load_arm_import_desc")

    def test_load_arm_import_desc_dot(self):
        logger.info("START: test_load_arm_import_desc_dot")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_IMPORT_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root, KINEMATIC_DESC_FOLDER)
        root = hyv[-1]
        G = create_dot_graph(root, composition=True, stereotype=True)
        path_dot = "test.png"
        logger.info("Writing to file: {}".format(path_dot))
        visualize_dot_graph(G, path_dot)
        #
        logger.info("END: test_load_arm_import_desc_dot")

    def test_load_arm_desc_queries(self):
        logger.info("START: test_load_arm_desc_queries")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_IMPORT_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root, KINEMATIC_DESC_FOLDER)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        kinematics_meta = hyv[0]
        link_element = kinematics_meta["elements"]["link"]
        joint_element = kinematics_meta["elements"]["joint"]
        rev_joint = kinematics_meta["rev_joint"]
        links = list(root.get_children(
            lambda x: x.stereotype is not None and (link_element.name in x.stereotype.nameset))
        )
        link_names = {'base_link', 'link_0', 'link_1', 'link_2', 'link_3', 'link_4', 'tool'}
        for n in link_names:
            logger.info(n)
            self.assertIn(n, [x.name for x in links])
        op = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "link_stereotype", 0
        )
        self.assertIsNotNone(op)
        res = op(link_element, root, depth=None)
        link_names = {'base_link', 'link_0', 'link_1', 'link_2', 'link_3', 'link_4', 'tool'}
        for n in link_names:
            self.assertIn(n, [x.name for x in res])
        # Check if the same result is obtained by passing the root as a stereotype
        op["stereotype"] = link_element
        res_2 = op(root, depth=None)
        for n in link_names:
            self.assertIn(n, [x.name for x in res])
        self.assertEqual(len(res), len(res_2))
        # Joints
        op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "joint_stereotype", 0,
            stereotype=joint_element
        )
        self.assertIsNotNone(op_joint)
        res_joint = op_joint(root)
        self.assertEqual(len(res_joint), 6)
        joint_names = {'j0', 'j1', 'j2', 'j3', 'j4', 'jtool'}
        for n in joint_names:
            self.assertIn(n, [x.name for x in res_joint])
        #
        logger.info("END: test_load_arm_desc_queries")

    def test_load_arm_desc_stereotpyes(self):
        logger.info("START: test_load_arm_desc_stereotpyes")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_IMPORT_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root, KINEMATIC_DESC_FOLDER)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        logger.info(root)
        kinematics_meta = hyv[0]
        link_element = kinematics_meta["elements"]["link"]
        joint_element = kinematics_meta["elements"]["joint"]
        rev_joint = kinematics_meta["rev_joint"]
        links = list(root.get_children(
            lambda x: x.stereotype is not None and (link_element.name in x.stereotype.nameset))
        )
        link_names = {'base_link', 'link_0', 'link_1', 'link_2', 'link_3', 'link_4', 'tool'}
        for n in link_names:
            self.assertIn(n, [x.name for x in links])
        # Joints
        rev_joints = list(root.get_children(
            lambda x: x.stereotype is not None and (rev_joint.name in x.stereotype.nameset))
        )
        joints = list(root.get_children(
            lambda x: x.stereotype is not None and (joint_element.name in x.stereotype.nameset))
        )
        logger.info("Joint names: {}".format([x.name for x in joints]))
        joint_names = {'j0', 'j1', 'j2', 'j3', 'j4', 'jtool'}
        for n in joint_names:
            self.assertIn(n, [x.name for x in joints])
        for n in joint_names:
            self.assertIn(n, [x.name for x in rev_joints])
        self.assertEqual(len(joints), len(rev_joints))
        logger.info("Stereotypes: {}".format(joints[0].stereotype.nameset))
        #
        logger.info("END: test_load_arm_desc_stereotpyes")

    def test_load_arm_desc_transform_urdf(self):
        logger.info("START: test_load_arm_desc_transform_urdf")
        #
        root = self.read_node(TEST_CASE_META_KINEMATICS_IMPORT_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root, KINEMATIC_DESC_FOLDER)
        root = hyv[-1]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        kinematics_meta = hyv[0]
        link_element = kinematics_meta["elements"]["link"]
        joint_element = kinematics_meta["elements"]["joint"]
        rev_joint = kinematics_meta["rev_joint"]
        op = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "link_stereotype", 0
        )
        self.assertIsNotNone(op)
        res = op(link_element, root, depth=None)
        link_names = {'base_link', 'link_0', 'link_1', 'link_2', 'link_3', 'link_4', 'tool'}
        for n in link_names:
            self.assertIn(n, [x.name for x in res])
        # Check if the same result is obtained by passing the root as a stereotype
        op["stereotype"] = link_element
        res_2 = op(root, depth=None)
        for n in link_names:
            self.assertIn(n, [x.name for x in res])
        self.assertEqual(len(res), len(res_2))
        # Joints
        op_joint = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            QueryIsStereotypeOperation, "joint_stereotype", 0,
            stereotype=joint_element
        )
        self.assertIsNotNone(op_joint)
        res_joint = op_joint(root)
        self.assertEqual(len(res_joint), 7)
        joint_names = {'j0', 'j1', 'j2', 'j3', 'j4', 'jtool'}
        for n in joint_names:
            self.assertIn(n, [x.name for x in res_joint])
        # XML serialization
        from lxml import etree
        op_transform_urdf = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            TransformationUrdf, "urdf_transformation", 0,
            kinematics_meta=kinematics_meta
        )
        res_xml = op_transform_urdf(root)
        self.assertIsNotNone(res_xml)
        print(etree.tostring(res_xml, pretty_print=True).decode("utf-8"))
        # Analyze the XML
        # Check if the root is robot
        self.assertEqual(res_xml.tag, "robot")
        # Write to file
        with open("test_urdf.xml", "w") as f:
            f.write(etree.tostring(res_xml, pretty_print=True).decode("utf-8"))
        #
        logger.info("END: test_load_arm_desc_transform_urdf")

    def test_load_with_hypergraph_loader(self):
        logger.info("START: test_load_with_hypergraph_loader")
        #
        paths = FactoryHypergraphElements.create_vertex_default("path_node", 0)
        paths["paths"] = [TEST_CASE_META_KINEMATICS_IMPORT_PARSING]
        paths["meta_elements"] = [TEST_CASE_META_KINEMATICS_PARSING]
        # Add hypergraph loader to the hypergraphloader
        hypergraph_loader = FactoryHypergraphElements.create_vertex_constructor_default(
            HypergraphLoader, "hypergraph_loader", 0
        )
        hypergraph_loader["path"] = paths
        res = hypergraph_loader()
        kinematics_meta, robot = res[0]
        print(robot.name)
        self.assertIsNotNone(res)
        link_names = {'base_link', 'link_0', 'link_1', 'link_2', 'link_3', 'link_4', 'tool'}
        # Factory URDF query
        query_factory = FactoryRobotQueryElements(kinematics_meta)
        # Req suery for
        op_link = query_factory.create_query_link_stereotype()
        self.assertIsNotNone(op_link)
        res = op_link(robot)

        for n in link_names:
            self.assertIn(n, [x.name for x in res])
        # Joints
        op_joint = query_factory.create_query_joint_stereotype()
        self.assertIsNotNone(op_joint)
        res_joint = op_joint(robot)
        self.assertEqual(len(res_joint), 7)
        joint_names = {'j0', 'j1', 'j2', 'j3', 'j4', 'jtool'}
        for n in joint_names:
            self.assertIn(n, [x.name for x in res_joint])



if __name__ == "__main__":
    unittest.main()


