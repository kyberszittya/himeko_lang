import time

from lang.himeko_meta_parser import Lark_StandAlone, Visitor, Transformer, v_args, Visitor_Recursive, Tree
from lang.identification.strategies import UidIdentificationStrategy, UuidIdentificationStrategy, \
    AbstractIdentificationStrategy
from lang.metaelements.himekoelement import AbstractClock, HimekoZygote
from lang.metaelements.himekonode import HimekoNode

inline_args = v_args(inline=True)

class SystemTimeClock(AbstractClock):

    def __init__(self):
        super().__init__()

    def tick(self) -> int:
        return time.time_ns()


class HimekoElementFactory(object):

    def __init__(self, clock=None):
        self.f_uid_id: AbstractIdentificationStrategy = UidIdentificationStrategy()
        self.f_uuid_id: AbstractIdentificationStrategy = UuidIdentificationStrategy()
        # Clock
        if clock is None:
            self.clock = SystemTimeClock()

    def search_for_string_element(self, t: Tree) -> str:
        r = next(t.find_data("string"))
        return str(r.children[0]).replace("\"","")

    def generate_himekonode(self, t: Tree):
        name = self.search_for_string_element(next(t.find_data("element_name")))
        zyg = HimekoZygote(name)
        genichrone = self.clock.nano_sec
        uid = self.f_uid_id.transform(zyg, "himekonode", genichrone)
        uuid = self.f_uuid_id.transform(zyg, "himekonoe", genichrone)
        return HimekoNode(name, uuid, uid)



class HypergraphTransformer(Transformer):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphVisitor(Visitor):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphRecursiveVisitor(Visitor_Recursive):

    def __init__(self):
        self.el_factory = HimekoElementFactory()

    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: self.el_factory.generate_himekonode(s)
    hi_edge = lambda self, s: print(s)


def main():
    p = "../examples/simple/minimal_example_with_edges.himeko"
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