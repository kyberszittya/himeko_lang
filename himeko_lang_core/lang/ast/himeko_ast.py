import sys
import typing
from typing import List
from dataclasses import dataclass

from lark import Lark, Transformer, v_args, ast_utils
from lark.tree import Tree

this_module = sys.modules[__name__]


class _Ast(ast_utils.Ast):
    pass


class _Statement(_Ast):
    pass

class Value(_Ast, ast_utils.WithMeta):
    pass



@dataclass
class ElementName(_Ast):
    name: str

@dataclass
class HiElementSignature(_Ast):
    name: ElementName


class _HiMetaelement(_Ast):
    name: ElementName

class HiMeta(_Ast):
    meta: _HiMetaelement



class _HiElement(_Ast):
    pass

@dataclass
class HiBody(_Ast):
    elements: List[_HiElement]


@dataclass
class Start(_Ast):
    name: HiMeta
    body: HiBody

@dataclass
class HiNode(_HiElement):
    signature: HiElementSignature
    children: typing.Optional[List[_HiElement]]

    def __init__(self, signature: HiElementSignature, *children: typing.Optional[List[_HiElement]]):
        self.signature = signature
        self.children = children



class ToAst(Transformer):
    @v_args(inline=True)
    def start(self, x):
        return x


transformer = ast_utils.create_transformer(this_module, ToAst())

