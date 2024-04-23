from lark import Lark, Transformer, v_args

from lang.ast.himeko_ast import transformer


def main(args=None):
    print(args)
    if args is None:
        p = "../../examples/simple/minimal_example_with_edges.himeko"
    else:
        p = args[0]
        print("Using path: "+p)
    parser = None
    with open("../HimekoMetalang.lark") as f:
        parser = Lark(''.join(f.readlines()), parser="lalr")
    with open(p) as f:
        tree = parser.parse(''.join(f.readlines()))
        print(tree.pretty())
        root = transformer.transform(tree)
        print(root)
        print(root.body.elements)


if __name__ == "__main__":
    main()