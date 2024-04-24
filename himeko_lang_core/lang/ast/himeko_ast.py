import sys
from typing import List
from dataclasses import dataclass

from lark import Transformer, v_args, ast_utils

this_module = sys.modules[__name__]


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
    relation_direction: Value
    reference: ElementReference

    def __init__(self, relation_direction: Value, reference: ElementReference):
        self.relation_direction = relation_direction
        self.reference = reference



@dataclass
class HiEdge(_HiAbstractElement):
    vertices: List[HiEdgeElement]

    def __init__(self, signature: HiElementSignature, *vertices: HiEdgeElement):
        super().__init__(signature)
        self.vertices = list(vertices)


@dataclass
class HiBody(_Ast):
    root: List[_HiAbstractElement]

    def __init__(self, *root: _HiAbstractElement):
        self.root = list(root)


@dataclass
class Start(_Ast):
    name: HiMeta
    body: HiBody


@dataclass
class HiNode(_HiAbstractElement):
    children: List[_HiAbstractElement]

    def __init__(self, signature: HiElementSignature, *children: _HiAbstractElement):
        super().__init__(signature)
        self.children = list(children)


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


def unfold_references(edge: HiEdge):

    for v in edge.vertices:
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


transformer = ast_utils.create_transformer(this_module, ToAst())

