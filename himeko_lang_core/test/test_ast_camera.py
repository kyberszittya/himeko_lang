import os

from himeko.hbcm.elements.edge import HyperEdge
from test_ancestor_testcase import ERROR_MSG_UNABLE_TO_TRANSFORM

from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_ancestor_testcase import TestAncestorTestCase

CAMERA_DESC_FOLDER = os.path.join("..", "robotics", "sensors")

TEST_CASE_CAMERA_PARSING = (
    os.path.join(CAMERA_DESC_FOLDER, "ip_camera.himeko"))


class TestBasicAstParsing(TestAncestorTestCase):

    def test_load_camera_desc(self):
        root = self.read_node(TEST_CASE_CAMERA_PARSING)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)[-1]
        self.assertIsNotNone(hyv, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(hyv.name, "ip_camera")
        meta = hyv["meta"]
        self.assertIsNotNone(meta, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(meta["model"].value, "DS-2CD2143G2-IU")
        self.assertEqual(meta["manufacturer"].value, "Hikvision")
        lenses = hyv["lenses"]
        # Check lens parameters
        lenses["lens"]
        self.assertEqual(lenses["lens"]["focal"].value, 2.4)
        self.assertEqual(lenses["lens_zoomed"]["focal"].value, 4.0)
        # FoV
        self.assertEqual(lenses["lens"]["field_of_view"]["horizontal"].value, 103)
        self.assertEqual(lenses["lens_zoomed"]["field_of_view"]["horizontal"].value, 84)
        # Check lens mount
        self.assertEqual(lenses["mount"].value, "M12")
        # Iris type
        self.assertEqual(lenses["iris_type"].value, "Fixed")
        # Stream parameters
        stream = hyv["stream"]
        self.assertTrue(stream["is_rtsp"].value)
        self.assertTrue(stream["is_onvif"].value)
        # H264 and H265
        self.assertTrue(stream["is_h264"].value)
        self.assertTrue(stream["is_h265"].value)
        # Check FPS and HZ
        self.assertEqual(stream["fps"].value, [25, 30])
        self.assertEqual(stream["hz"].value, [50, 60])
        # Edge
        edge = hyv["resolution_images"]
        self.assertIsNotNone(edge, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertIsInstance(edge, HyperEdge)
        self.assertEqual(edge.name, "resolution_images")
        out_2 = list(edge.out_relations())
        self.assertEqual(len(out_2), 2)
        self.assertEqual(out_2[0].target.name, "ir_sensor")
        self.assertEqual(out_2[1].target.name, "rgb_sensor")
        # Check incoming relations
        in_1 = list(edge.in_relations())
        self.assertEqual(len(in_1), 1)
        self.assertEqual(in_1[0].target.name, "resolution")
        # Check network connection (edge)
        network = hyv["network_connection"]
        self.assertIsNotNone(network, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertIsInstance(network, HyperEdge)
        self.assertEqual(network.name, "network_connection")
        out_1 = list(network.out_relations())
        self.assertEqual(len(out_1), 1)
        self.assertEqual(out_1[0].target.name, "network")
        # Check incoming relations
        in_2 = list(network.in_relations())
        self.assertEqual(len(in_2), 1)
        self.assertEqual(in_2[0].target.name, "stream")
