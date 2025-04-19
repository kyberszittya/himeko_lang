import os

from himeko.hbcm.elements.edge import HyperEdge
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from .test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM
from .test_case_descriptions import TEST_CASE_SIMPLE_FOLDER


class TestBasicAstParsing(TestAncestorTestCase):

    def test_copy_values(self):
        p = os.path.join(TEST_CASE_SIMPLE_FOLDER, "attr", "example_value_copy_relations.himeko")
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        self.assertEqual(context.name, "context")
        e_val = context["node_lev_0"]["e0"]
        self.assertEqual(e_val.name, "e0")
        self.assertEqual(e_val.parent.name, "node_lev_0")
        self.assertIsInstance(e_val, HyperEdge)
        # Out relations
        out_relations = list(e_val.out_relations())
        self.assertEqual(len(out_relations), 3)
        self.assertEqual(out_relations[0].value, [0.0, 0.0, 0.0])
        self.assertEqual(out_relations[1].value, [0.0, 0.0, 0.0])
        self.assertEqual(out_relations[2].value, [[0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]])
        # Change some values
        out_relations[0].value[0] = 1.0
        out_relations[0].value[1] = 18.0
        self.assertEqual(out_relations[0].value, [1.0, 18.0, 0.0])
        self.assertEqual(out_relations[1].value, [0.0, 0.0, 0.0])
        self.assertEqual(out_relations[2].value, [[0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0]])
        # Change some other values
        out_relations[2].value[0][0] = 42.0
        out_relations[2].value[0][1] = 242.0
        out_relations[2].value[1][0] = -52.0
        out_relations[2].value[1][1] = -89.0
        out_relations[2].value[1][2] = 174.0
        self.assertEqual(out_relations[0].value, [1.0, 18.0, 0.0])
        self.assertEqual(out_relations[1].value, [0.0, 0.0, 0.0])
        self.assertEqual(out_relations[2].value, [[42.0, 242.0, 1.0], [-52.0, -89.0, 174.0, 1.0]])
