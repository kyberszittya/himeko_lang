import os

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
        hyv = hbcm_mapper.convert_tree(root)
        print(hyv)