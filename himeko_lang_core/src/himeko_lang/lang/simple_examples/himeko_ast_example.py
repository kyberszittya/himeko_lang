from lark import Lark

from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_ast.himeko_ast import transformer, collect_edges, create_ast


def main(args=None):
    if args is None:
        p = "../../examples/simple/minimal_example_with_hierarchy_ref_edges_with_values.himeko"
    else:
        p = args[0]
        print("Using path: " + p)
    parser = None
    with open("../HimekoMetalang.lark") as f:
        parser = Lark(''.join(f.readlines()), parser="lalr")
    with open(p) as f:
        tree = parser.parse(''.join(f.readlines()))
        root = transformer.transform(tree)

        create_ast(root)
        for e in collect_edges(root.body.root[0]):
            for rel in e.children:
                print(rel.raw_relation_direction, rel.reference.reference.signature.name.value)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.create_root_hyper_vertices(root)
        hbcm_mapper.create_edges(root)
        hbcm_mapper.create_attributes(root)
        for context in hyv:
            print(context.name)
            nodes = context.get_children(lambda x: isinstance(x, HyperVertex), None)
            node_names = set(map(lambda x: x.name, nodes))
            print(node_names)
            for e in nodes:
                print(e.name, e.parent.name)
            edges = context.get_children(lambda x: isinstance(x, HyperEdge), None)
            for e in edges:
                print(e.name, e.parent.name)
                for r in e.all_relations():
                    print(r.direction, r.target.name, r.target.parent.name)
            attrs = context.get_children(lambda x: isinstance(x, HypergraphAttribute), None)
            for a in attrs:
                print(a.name, a.value)


if __name__ == "__main__":
    main()
