from dataclasses import dataclass

from lang.himeko_ast.elements.meta_elements import _Ast
from lang.himeko_ast.elements.reference import ElementReference


@dataclass
class ElementType(_Ast):
    value: ElementReference

    def __init__(self, value: ElementReference):
        self.value = value


@dataclass
class HiType(_Ast):
    type: ElementType

    def __init__(self, value: ElementType):
        self.type = value