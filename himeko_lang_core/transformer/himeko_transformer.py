
from lang.himeko_meta_parser import Lark_StandAlone, Visitor, Transformer, v_args, Visitor_Recursive, Tree
from lang.identification.strategies import UidIdentificationStrategy, UuidIdentificationStrategy, \
    AbstractIdentificationStrategy
from lang.metaelements.himekonode import HimekoNode

inline_args = v_args(inline=True)

class HimekoElementFactory(object):
    uid_id: AbstractIdentificationStrategy = UidIdentificationStrategy()
    uuid_id: AbstractIdentificationStrategy = UuidIdentificationStrategy()

    @staticmethod
    def generate_himekonode(t: Tree):
        for x in t.children:
            print(x.children)




class HypergraphTransformer(Transformer):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphVisitor(Visitor):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphRecursiveVisitor(Visitor_Recursive):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: HimekoElementFactory.generate_himekonode(s)
    hi_edge = lambda self, s: print(s)


def main():
    p = "../examples/simple/minimal_example.himeko"
    # Transformer
    parser = Lark_StandAlone(transformer=HypergraphTransformer())

    with open(p) as f:
        tree = parser.parse(f.read())
        print(tree.pretty())

    # Visitor
    parser = Lark_StandAlone()
    with open(p) as f:
        tree = parser.parse(f.read())
        print(tree.pretty())
        visitor = HypergraphVisitor()
        rvisitor = HypergraphRecursiveVisitor()
        visitor.visit(tree)
        rvisitor.visit_topdown(tree)



if __name__ == "__main__":
    main()