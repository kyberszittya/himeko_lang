from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

from lang.himeko_meta_parser import Visitor_Recursive
from transformer.common.lark_tree_extractor import LarkElementMetaHimekoExtractor


class HimekoHbcmTransformer(Visitor_Recursive):

    __le_ext = LarkElementMetaHimekoExtractor
    __hi_fact = FactoryHypergraphElements

    def __init__(self):
        super().__init__()
        self.nodes = set()

    def visit_hi_node(self, s):
        self.nodes.add(s)
        __name = self.__le_ext.get_element_name(s)
        # TODO: from here
        self.__hi_fact.create_vertex_constructor_default_kwargs(HyperVertex, __name, )


    hi_node = lambda self, s: self.visit_hi_node(s)
    hi_metaelement = lambda self, s: None
    hi_element_field =  lambda self, s: None
    hi_edge = lambda self, s: None

