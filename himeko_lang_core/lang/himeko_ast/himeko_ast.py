import sys
import time
import typing
from typing import List
from dataclasses import dataclass

from lark import Transformer, v_args, ast_utils
from enum import Enum

from himeko.hbcm.elements.edge import HyperEdge, ReferenceQuery
from himeko.hbcm.elements.vertex import HyperVertex

this_module = sys.modules[__name__]



class AstEnumRelationDirection(Enum):
    UNDEFINED = 0
    IN = 1
    OUT = 2
    UNDIRECTED = 3


class _Ast(ast_utils.Ast):
    pass


class _Statement(_Ast):
    pass


class Value(_Ast, ast_utils.WithMeta):
    pass


def enumerate_direction(arg):
    match arg:
        case '--': return AstEnumRelationDirection.UNDEFINED
        case '->': return AstEnumRelationDirection.OUT
        case '<-': return AstEnumRelationDirection.IN
        case '<>': return AstEnumRelationDirection.UNDIRECTED

@dataclass
class ElementName(_Ast):
    value: str

@dataclass
class ElementReference(_Ast):
    name: str

    def __init__(self, *args):
        if len(args) == 1:
            self.direction = None
            self.name = args[0].replace('"', '')
            self.direction = AstEnumRelationDirection.UNDEFINED
            self.value = 1.0
        elif len(args) == 2:
            direction, name = args
            self.direction = enumerate_direction(str(direction.value))
            self.name = name.replace('"', '')
            self.value = 1.0
        elif len(args) == 3:
            direction, name, value = args
            self.direction = enumerate_direction(str(direction.value))
            self.name = name.replace('"', '')
            self.value = value
        self._reference = None

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value


@dataclass
class HiTemplating(_Ast):
    reference = ElementReference

    def __init__(self, reference: ElementReference):
        self.reference = reference


@dataclass
class HiElementSignature(_Ast):
    name: ElementName
    template: HiTemplating

    def __init__(self, name: ElementName, template: HiTemplating = None):
        self.name = name
        self.template = template


class _HiMetaelement(_Ast):
    name: ElementName


class HiMeta(_Ast):
    meta: _HiMetaelement


@dataclass
class _TreeElement(_Ast):

    def __init__(self):
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value


@dataclass
class _HiAbstractElement(_TreeElement):
    signature: HiElementSignature

    def __init__(self, signature: HiElementSignature):
        super().__init__()
        self.signature = signature

@dataclass
class _HiNodeElement(_Ast):
    hi_node_element: _HiAbstractElement


@dataclass
class HiElementValue(_TreeElement):
    value: Value

    def __init__(self, value: Value):
        super().__init__()
        self.value = value


@dataclass
class ElementType(_Ast):
    type: Value

    def __init__(self, value: Value):
        self.type = value


@dataclass
class VectorField(_Ast):
    value: typing.List[HiElementValue]

    def __init__(self, *value):
        self.value = list(value)


@dataclass
class HiElementField(_TreeElement):
    name: ElementName
    type: typing.Optional[ElementType]
    value: typing.Optional[HiElementValue | VectorField]

    def __init__(self, name: ElementName,
                 *args):
        super().__init__()
        self.name = name
        self.type = None
        self.value = None
        if len(args) == 2:
            self.type = args[0]
            self.value = args[1]
        elif len(args) == 1:
            if isinstance(args[0], ElementType):
                self.type = args[0]
                self.value = None
            else:
                self.type = None
                self.value = args[0]



@dataclass
class HiEdgeElement(_Ast):
    value: typing.Optional[VectorField]
    relation_direction: AstEnumRelationDirection
    reference: ElementReference

    def __init__(self, arg):
        # Check for type of arg (element reference, element field, edge)
        if isinstance(arg, ElementReference):
            self.value = arg.value
            self.relation_direction = arg.direction
            self.reference = arg
        elif isinstance(arg, HiElementField):
            # Todo: add value in a parent relationship
            self.value = arg.value
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None
        elif isinstance(arg, HiEdge):
            # TODO: add edge in a parent relationship
            self.value = arg
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None


@dataclass
class HiEdge(_HiAbstractElement):
    relationships: List[HiEdgeElement]

    def __init__(self, hi_edge_type, signature: HiElementSignature, *vertices: HiEdgeElement):
        super().__init__(signature)
        self.edge_type = hi_edge_type
        self.relationships = list(vertices)


@dataclass
class HiBody(_Ast):
    root: List[_HiAbstractElement]

    def __init__(self, *root: _HiAbstractElement):
        self.root = list(root)


@dataclass
class Start(_Ast):
    name: HiMeta
    body: HiBody


def extract_root_context(ast: Start):
    return ast.body.root


@dataclass
class HiNode(_HiAbstractElement):
    children: List[_HiAbstractElement]
    timestamp: int

    def __init__(self, signature: HiElementSignature, *children):
        super().__init__(signature)
        self.children = list([x.children[0] for x in children])
        self.timestamp = time.time_ns()

    def __hash__(self):
        hashed = [str(self.signature.name.value), self.timestamp]
        hashed.extend([str(c.signature.name.value) for c in
                       filter(lambda x: isinstance(x, HyperVertex) or isinstance(x, HyperEdge), self.children)])
        if self.parent is not None:
            hashed.append(str(self.parent.signature.name.value))
        return hash(tuple(hashed))


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

