from lark import Lark

from lang.ast.himeko_ast import transformer, set_parents, collect_leafs, HiNode, HiEdge, unfold_references


def main(args=None):
    if args is None:
        p = "../../examples/simple/minimal_example_with_edges.himeko"
    else:
        p = args[0]
        print("Using path: " + p)
    parser = None
    with open("../HimekoMetalang.lark") as f:
        parser = Lark(''.join(f.readlines()), parser="lalr")
    with open(p) as f:
        tree = parser.parse(''.join(f.readlines()))
        root = transformer.transform(tree)
        set_parents(root.body.root[0])
        leafs = collect_leafs(root.body.root[0])
        for leaf in leafs:
            if isinstance(leaf, HiNode):
                print("Node: ", leaf.signature.name.value, leaf.parent.signature.name.value)
            elif isinstance(leaf, HiEdge):
                print("Edge: ", leaf.signature.name.value, leaf.parent.signature.name.value)
                unfold_references(leaf)
                for v in leaf.vertices:
                    print("Unfolded ref:", v.reference.reference.signature.name.value, v.reference.reference.parent.signature.name.value)



if __name__ == "__main__":
    main()
