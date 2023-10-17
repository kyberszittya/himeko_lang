from lark import Lark

def main():
    p = "../examples/simple/minimal_example_with_edges.himeko"
    parser = None
    with open("HimekoMetalang.lark") as f:
        parser = Lark(''.join(f.readlines()), parser="lalr")
    with open(p) as f:
        tree = parser.parse(''.join(f.readlines()))
        print(tree.pretty())


if __name__ == "__main__":
    main()