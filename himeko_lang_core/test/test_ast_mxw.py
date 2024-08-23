from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.mxw.mxw_scene import TransformationMxw
from test_ancestor_testcase import TestAncestorTestCase

from himeko.common.clock import NullClock
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer


class TestMaxwhereTransformation(TestAncestorTestCase):

    def test_node_maxwhere_simple_scene1(self):
        p = "../examples/mxw/mxw_cylinder.himeko"
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root, "../examples/mxw/")
        root = hyv[-1]
        self.assertEqual(root.name, "munkahenger_scene")
        self.assertEqual(root["munkahenger"], "munkahenger")
        mxw_meta = hyv[0]
        op_transformation_mxw_scene = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            TransformationMxw, "transformation_mxw", 0,
            mxw_meta=mxw_meta
        )
        res_jsx = op_transformation_mxw_scene(root)
