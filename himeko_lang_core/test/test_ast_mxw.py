from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.mxw.mxw_scene import TransformationMxw
from test_ancestor_testcase import TestAncestorTestCase

from himeko.common.clock import NullClock
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer


class TestMaxwhereTransformation(TestAncestorTestCase):

    def test_node_maxwhere_simple_scene1(self):
        p = "../examples/mxw/mxw_cylinder.himeko"
        root = self.read_node(p)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root, "../examples/mxw/")
        root = hyv[-1]
        self.assertEqual(root.name, "munkahenger_scene")
        self.assertIsNotNone(root["munkahenger"])
        self.assertEqual(root["munkahenger"].name, "munkahenger")
        self.assertIsNotNone(root["munkahenger"]["munkahenger_base"])
        self.assertEqual(root["munkahenger"]["munkahenger_base"].name, "munkahenger_base")
        self.assertIsNotNone(root["munkahenger"]["munkahenger_moving"])
        self.assertEqual(root["munkahenger"]["munkahenger_moving"].name, "munkahenger_moving")
        # Assert correct position
        self.assertEqual(root["munkahenger"]["position"].value, [600, 0, 600])
        self.assertEqual(root["munkahenger"]["orientation"].value, [90, 0, 0])
        mxw_meta = hyv[0]
        op_transformation_mxw_scene = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
            TransformationMxw, "transformation_mxw", 0,
            mxw_meta=mxw_meta, units=root["units"]
        )
        res_jsx = op_transformation_mxw_scene(root)
        print(res_jsx)
        with open(f"{root.name}.jsx", "w") as f:
            f.write(res_jsx)
