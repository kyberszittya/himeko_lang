from himeko.common.clock import NullClock
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.mxw.mxw_scene import TransformationMxw
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_ast.himeko_ast import transformer
from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone


def read_node(path):
    # Transformer
    parser = Lark_StandAlone(transformer=transformer)
    # Read file
    with open(path) as f:
        tree = parser.parse(f.read())
    return tree

def main():
    p = "../examples/mxw/mxw_cylinder.himeko"
    root = read_node(p)
    hbcm_mapper = AstHbcmTransformer(NullClock())
    hyv = hbcm_mapper.convert_tree(root, "../examples/mxw/")
    root = hyv[-1]
    mxw_meta = hyv[0]
    op_transformation_mxw_scene = FactoryHypergraphElements.create_vertex_constructor_default_kwargs(
        TransformationMxw, "transformation_mxw", 0,
        mxw_meta=mxw_meta, units=root["units"]
    )
    res_jsx = op_transformation_mxw_scene(root)
    print(res_jsx)
    with open(f"{root.name}.jsx", "w") as f:
        f.write(res_jsx)

if __name__ == "__main__":
    main()