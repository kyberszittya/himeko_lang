import sys
import time
from typing import List
from dataclasses import dataclass

from lark import Transformer, v_args, ast_utils
from enum import Enum

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


@dataclass
class ElementName(_Ast):
    value: str


@dataclass
class HiElementSignature(_Ast):
    name: ElementName


class _HiMetaelement(_Ast):
    name: ElementName


class HiMeta(_Ast):
    meta: _HiMetaelement


@dataclass
class _HiAbstractElement(_Ast):
    signature: HiElementSignature

    def __init__(self, signature: HiElementSignature):
        self.signature = signature
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value


@dataclass
class ElementReference(_Ast):
    name: str

    def __init__(self, name):
        self.name = name.replace('"', '')
        self._reference = None

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value


@dataclass
class HiEdgeElement(_Ast):
    raw_relation_direction: Value
    relation_direction: AstEnumRelationDirection
    reference: ElementReference

    def __init__(self, relation_direction: Value, reference: ElementReference):
        self.raw_relation_direction = relation_direction
        match relation_direction:
            case '--': self.relation_direction = AstEnumRelationDirection.UNDEFINED
            case '->': self.relation_direction = AstEnumRelationDirection.OUT
            case '<-': self.relation_direction = AstEnumRelationDirection.IN
            case '<>': self.relation_direction = AstEnumRelationDirection.UNDIRECTED
        self.reference = reference


@dataclass
class HiEdge(_HiAbstractElement):
    relationships: List[HiEdgeElement]

    def __init__(self, signature: HiElementSignature, *vertices: HiEdgeElement):
        super().__init__(signature)
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

    def __init__(self, signature: HiElementSignature, *children: _HiAbstractElement):
        super().__init__(signature)
        self.children = list(children)
        self.timestamp = time.time_ns()

    def __hash__(self):
        hashed = [str(self.signature.name.value), self.timestamp]
        hashed.extend([str(c.signature.name.value) for c in self.children])
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
            unfold_references(n)


def unfold_references(edge: HiEdge):
    for v in edge.relationships:
        context_name = v.reference.name.split('.')[::-1]
        context = edge
        for _ in context_name:
            context = context.parent
        # Backfold
        node = None
        for c in context_name[::-1]:
            for n in context.children:
                # Node found in context getting deeper
                if n.signature.name.value == c:
                    node = n
                    break
            # Update context
            context = node
        if node is not None:
            v.reference.reference = node


def create_ast(start: Start):
    for v in extract_root_context(start):
        if isinstance(v, HiNode):
            set_parents(v)
            unfold_references_in_context(v)


transformer = ast_utils.create_transformer(this_module, ToAst())
