import typing

from dataclasses import dataclass

from lang.himeko_ast.elements.meta_elements import _TreeElement, _Ast, ElementName
from lang.himeko_ast.elements.stereotype import HiStereotype
from lang.himeko_ast.elements.use_element import HiUse


@dataclass
class HiElementSignature(_Ast):
    name: ElementName
    template: typing.Optional[HiStereotype]
    usage: typing.List[typing.Optional[HiUse]]

    def __init__(self, name: ElementName, *args):
        self.name = name
        self.template = None
        self.usage = []
        if len(args) == 1:
            if isinstance(args[0], HiStereotype):
                self.template = args[0]
            else:
                self.usage.append(args[0])
        elif len(args) >= 2:
            for a in args:
                if isinstance(a, HiStereotype):
                    self.template = a
                elif isinstance(a, HiUse):
                    self.usage.append(a)


@dataclass
class _HiAbstractElement(_TreeElement):
    signature: HiElementSignature

    def __init__(self, signature: HiElementSignature):
        super().__init__()
        self.signature = signature
