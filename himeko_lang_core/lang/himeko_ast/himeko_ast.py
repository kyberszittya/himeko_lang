import sys
from typing import List
from dataclasses import dataclass

from lark import Transformer, v_args, ast_utils

from himeko.hbcm.elements.edge import ReferenceQuery
from lang.himeko_ast.elements.abstract_elements import HiElementSignature, _HiAbstractElement
from lang.himeko_ast.elements.graph.elementfield import HiElementField
from lang.himeko_ast.elements.graph.hiedge import HiEdgeElement, HiEdge
from lang.himeko_ast.elements.graph.hinode import _HiNodeElement, HiNode
from lang.himeko_ast.elements.meta_elements import _Ast, _Statement, Value, ElementName, HiIncludePath, HiInclude, \
    HiMetaelement, _TreeElement
from lang.himeko_ast.elements.reference import ElementReference
from lang.himeko_ast.elements.stereotype import HiStereotype
from lang.himeko_ast.elements.types.data_type import ValueType, HiElementValue, VectorField
from lang.himeko_ast.elements.types.element_type import ElementType, HiType
from lang.himeko_ast.elements.use_element import HiUse

ast_types = [
    # Main elements
    HiElementSignature, _HiAbstractElement, # Abstract elements
    _Ast, _Statement, Value, ElementName, HiIncludePath, HiInclude, HiMetaelement, _TreeElement, # Meta elements
    ElementReference, # Reference
    HiStereotype, # Stereotype
    HiUse, # Use
    # Graph elements
    HiElementField, # Element field
    HiEdgeElement, HiEdge, # Edge
    _HiNodeElement, HiNode, # Node
    # Typing
    ValueType, HiElementValue, VectorField, # Data type
    ElementType, HiType, # Element type
]


this_module = sys.modules[__name__]

@dataclass
class HiMeta(_Ast):
    meta: HiMetaelement

    def __init__(self, meta: HiMetaelement, *args):
        super().__init__()
        self.meta = meta


@dataclass
class HiBody(_Ast):
    root: List[_HiAbstractElement]

    def __init__(self, *root: _HiAbstractElement):
        self.root = list(root)


@dataclass
class Start(_Ast):
    meta: HiMeta
    body: HiBody


def extract_root_context(ast: Start):
    return ast.body.root

def extract_meta_context(ast: Start):
    return ast.meta





class ToAst(Transformer):
    @v_args(inline=True)
    def start(self, x):
        return x


def set_parents(node: HiNode):
    for n in node.children:
        n.parent = node
        if isinstance(n, HiNode):
            set_parents(n)
        elif isinstance(n, HiEdge):
            n.parent = node


def collect_leafs(node: HiNode):
    leafs = []
    for n in node.children:
        if isinstance(n, HiNode) and len(n.children) > 0:
            leafs.extend(collect_leafs(n))
        elif isinstance(n, HiNode) and len(n.children) == 0:
            leafs.append(n)
        elif isinstance(n, HiEdge):
            leafs.append(n)
    return leafs


def collect_edges(node: HiNode):
    edges = []
    for n in node.children:
        if isinstance(n, HiNode) and len(n.children) > 0:
            edges.extend(collect_edges(n))
        elif isinstance(n, HiEdge):
            edges.append(n)
    return edges


def unfold_references_in_context(node: HiNode):
    for n in node.children:
        if isinstance(n, HiNode):
            unfold_references_in_context(n)
        elif isinstance(n, HiEdge):
            convert_references(n)


def convert_references(edge: HiEdge):
    for v in edge.relationships:
        v.reference.reference = ReferenceQuery(v.reference.name)


def create_ast(start: Start):
    for v in extract_root_context(start):
        if isinstance(v, HiNode):
            set_parents(v)
    # Unfold references
    for v in extract_root_context(start):
        if isinstance(v, HiNode):
            unfold_references_in_context(v)


transformer = ast_utils.create_transformer(this_module, ToAst())

