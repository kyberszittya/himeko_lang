import typing
from dataclasses import dataclass

from himeko_lang.lang.himeko_ast.elements.meta_elements import _Ast, _TreeElement, Value

@dataclass
class ValueType(_Ast):
    value: str

    def __init__(self, value: str):
        self.value = value


@dataclass
class HiElementValue(_TreeElement):
    value: Value

    def __init__(self, value: Value):
        super().__init__()
        self.value = value

@dataclass
class VectorField(_Ast):
    value: typing.List[HiElementValue]

    def __init__(self, *value):
        self.value = list(value)
