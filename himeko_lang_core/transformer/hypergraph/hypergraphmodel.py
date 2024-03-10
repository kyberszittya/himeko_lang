import time

from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

from lang.himeko_meta_parser import Visitor_Recursive, Tree
from transformer.common.lark_tree_extractor import LarkElementMetaHimekoExtractor



class HimekoHbcmTransformer(Visitor_Recursive):

    __le_ext = LarkElementMetaHimekoExtractor
    __hi_fact = FactoryHypergraphElements

    def __init__(self):
        super().__init__()
        self.nodes = set()

    """
    Visit a hypergraph node in the description
    
    :param tree: the LARK tree node
    :type tree: Tree
    :return: created element
    
    @startuml
    |LARK parser|
    start
    
    :Vist hierarchical tree topdown;
    |HBCM transformer|
    :Extract element name;
    if (element name in visited nodes) then (yes)
        stop;
    endif
    :Create new node as a temporary element;
    :Extract subelements (hierarchy)\ninto queue;
    
    repeat
        :Extract subnode element signature;
        :Add subnode element signature to \nthe current node children;
            
    repeat while (for each subnode) is (not empty) not (elements extracted)
    
    stop
    
    @enduml
    
    """
    def visit_hi_node(self, tree: Tree):
        __name = self.__le_ext.get_meta_element_name(tree)
        # TODO: from here
        t0 = time.time_ns()
        if __name not in self.nodes:
            new_node = self.__hi_fact.create_vertex_constructor_default_kwargs(HyperVertex, __name, t0)
            # TODO identification
            print(new_node)

    hi_node = lambda self, s: self.visit_hi_node(s)
    hi_metaelement = lambda self, s: None
    hi_element_field =  lambda self, s: None
    hi_edge = lambda self, s: None

