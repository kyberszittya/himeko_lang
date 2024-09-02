import typing
from dataclasses import dataclass

from lang.himeko_ast.elements.meta_elements import _TreeElement, ElementName
from lang.himeko_ast.elements.types.data_type import VectorField, HiElementValue
from lang.himeko_ast.elements.types.element_type import ElementType, HiType


@dataclass
class HiElementField(_TreeElement):
    name: ElementName
    type: typing.Optional[ElementType]
    value: typing.Optional[HiElementValue | VectorField]

    def __init__(self, name: ElementName, *args):
        super().__init__()
        self.name = name
        self.type = None
        self.value = None
        if len(args) == 2:
            self.type = args[0].type
            self.value = args[1]
        elif len(args) == 1:
            if isinstance(args[0], HiType):
                self.type = args[0].type
                self.value = None
            else:
                self.type = None
                self.value = args[0]
