import time

from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

from himeko_lang.lang.himeko_meta_parser import Visitor_Recursive, Tree
from himeko_lang.transformer.common.lark_tree_extractor import LarkElementMetaHimekoExtractor



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
    :Initialize **__visited set__**={0};    
    repeat
    :**__n0__** := Select node;
    
    :Vist hierarchical tree topdown;
    |HBCM transformer|
    :Extract element name from **__n0__**;
    if (element name in visited nodes) then (yes)
        stop;
    endif
    :Create new node **__h0__** as a temporary element;
    :Extract subelements (hierarchy)\ninto queue;
    
    repeat
        :Extract subnode element signature from **__nsub0__**;
        :Add subnode element signature to \nthe current node children as subelement;
        :Track **__n0__** node as parent for each node;
            
    repeat while (for each subnode **__nsub0__**) is (not empty) not (elements extracted)
    
    :Generate identification code for node\nBased on (Prüfer code) 
       - name
       - parent name
       - parent initial code
       - initial element count
    ;
    :Generate identification code on subelement\n composition change (add/remove);
    |LARK parser|
    repeat while (for each node element) is (leaf node) not (end of tree)
    
    stop
    
    @enduml
    
    """
    def visit_hi_node(self, tree: Tree):
        __name = self.__le_ext.get_meta_element_name(tree)
        t0 = time.time_ns()
        # If parent is defined
        parent = None
        if hasattr(tree, "parent"):
            print()
        # New node
        new_node = self.__hi_fact.create_vertex_constructor_default_kwargs(HyperVertex, __name, t0)
        # Iterate children
        for nsub0 in filter(lambda x: x.data == "hi_element", tree.children):
            print(nsub0)
            # Add subnode element signature to the current node children as subelement
            #new_node.add_children(self.visit(nsub0))



    """
    Initialize hypertree structure
    """
    def __default__(self, tree):
        __name = next(tree.find_data("element_name")).children[0]
        for subtree in filter(lambda x:
                              isinstance(x, Tree) and x.data == "hi_node",
                              tree.children):
            subtree: Tree
            subtree.parent = tree
            __name = next(subtree.find_data("element_name")).children[0]

    hi_node = lambda self, s: self.visit_hi_node(s)
    hi_metaelement = lambda self, s: None
    hi_element_field = lambda self, s: None
    hi_edge = lambda self, s: None

