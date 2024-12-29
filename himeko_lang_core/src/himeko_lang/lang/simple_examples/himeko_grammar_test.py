from lark import Lark
import sys

from himeko_lang.transformer.himeko_transformer import HypergraphVisitor


"""
This is a test file for the Himeko Metalang. It is used to test the Lark parser and the transformer.

example arg: "../../examples/simple/minimal_example_with_edges.himeko" 
"""
def main(args=None):
    print(args)
    if args is None:
        p = ["../../examples/simple/minimal_example_with_edges.himeko"]
    else:
        p = args[0]
        print("Using path: "+p)
    parser = None
    with open("../HimekoMetalang.lark") as f:
        parser = Lark(''.join(f.readlines()), parser="lalr")
    with open(p) as f:
        tree = parser.parse(''.join(f.readlines()))
        print(tree.pretty())
        transformer = HypergraphVisitor()
        transformer.visit(tree)


if __name__ == "__main__":
    main(sys.argv[1:])