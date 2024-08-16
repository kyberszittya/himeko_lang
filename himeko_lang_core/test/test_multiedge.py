import os


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