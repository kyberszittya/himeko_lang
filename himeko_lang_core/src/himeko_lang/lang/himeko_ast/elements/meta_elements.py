from enum import Enum
from lark import ast_utils
from dataclasses import dataclass
import typing


class AstEnumRelationDirection(Enum):
    UNDEFINED = 0
    IN = 1
    OUT = 2
    UNDIRECTED = 3

class AstEnumRefereneModifier(Enum):
    COPY = 0
    USE = 1
    EXTEND = 2


class _Ast(ast_utils.Ast):
    pass


class _Statement(_Ast):
    pass

class RelationDirection(_Ast):
    direction: AstEnumRelationDirection

    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            self.direction = enumerate_direction(args[0])
        elif len(args) == 1 and isinstance(args[0], AstEnumRelationDirection):
            self.direction = args[0]
        else:
            raise ValueError("Invalid arguments for RelationDirection, expected a string or AstEnumRelationDirection instance.")


class Value(_Ast, ast_utils.WithMeta):
    pass



def enumerate_direction(arg):
    match arg:
        case '~': return AstEnumRelationDirection.UNDEFINED
        case '-': return AstEnumRelationDirection.OUT
        case '=': return AstEnumRelationDirection.OUT
        case '+': return AstEnumRelationDirection.IN
        case '->': return AstEnumRelationDirection.IN
        case '<>': return AstEnumRelationDirection.UNDIRECTED


def enumerate_modifier(arg):
    match arg:
        case '<<copy>>': return AstEnumRefereneModifier.COPY
        case '|>': return AstEnumRefereneModifier.COPY
        case '<<use>>': return AstEnumRefereneModifier.USE
        case '*|>': return AstEnumRefereneModifier.USE
        case '<<extend>>': return AstEnumRefereneModifier.EXTEND
        case '-|>': return AstEnumRefereneModifier.EXTEND

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

    def __init__(self, name: ElementName, *args):
        self.name = name


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



