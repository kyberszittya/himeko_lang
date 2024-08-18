from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_case_descriptions import TEST_CASE_SIMPLE_FOLDER

from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM

import os


TEST_CASE_MINIMAL_DEGREE_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_structure_simple_coding.himeko")
)

TEST_CASE_MINIMAL_DEO_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_very_simple_1.himeko")
)

class TestBasicAstParsing(TestAncestorTestCase):

    def test_leaf_elements(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEGREE_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n0")
        leafs = set(root.get_leaf_elements())
        name_set = set([x.name for x in leafs])
        self.assertIn("n4", name_set)
        self.assertIn("n6", name_set)
        self.assertIn("n9", name_set)
        self.assertIn("n8", name_set)
        self.assertIn("n10", name_set)
        self.assertIn("n12", name_set)
        self.assertIn("n13", name_set)
        # Assert some elements not in the set
        self.assertNotIn("n0", name_set)
        self.assertNotIn("n1", name_set)
        self.assertNotIn("n2", name_set)
        self.assertNotIn("n3", name_set)
        self.assertNotIn("n5", name_set)
        self.assertNotIn("n7", name_set)
        self.assertNotIn("n11", name_set)


    def test_label_coding(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n2")
        # Collect leaves
        leafs = list(root.get_leaf_elements())
        print([x.name for x in leafs])

