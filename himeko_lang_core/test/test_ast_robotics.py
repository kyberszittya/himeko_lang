import os

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
        print(hyv)