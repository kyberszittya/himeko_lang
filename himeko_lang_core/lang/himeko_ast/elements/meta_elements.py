from enum import Enum
from lark import ast_utils
from dataclasses import dataclass
import typing


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
class HiIncludePath(_Ast):
    value: str

    def __init__(self, value):
        self.value = value


def sanitize_string(value):
    return value.replace('"', '')


@dataclass
class HiInclude(_Ast):
    value: str

    def __init__(self, path: HiIncludePath):
        self.value = sanitize_string(str(path.value))


class HiMetaelement(_Ast):
    name: ElementName
    includes: typing.List[HiInclude]

    def __init__(self, name: ElementName, *args):
        self.name = name
        self.includes = list(filter(lambda x: isinstance(x, HiInclude), args))


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



