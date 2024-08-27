from dataclasses import dataclass


from lang.himeko_ast.elements.meta_elements import AstEnumRelationDirection, _Ast, enumerate_direction
from lang.himeko_ast.elements.types.data_type import VectorField


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
            self.name = name.replace('"', '')
            # Check if we have a value instead of direction
            if isinstance(direction, VectorField):
                self.direction = AstEnumRelationDirection.UNDEFINED
                self.value = direction
            else:
                # Else a simple relation is defined
                self.direction = enumerate_direction(str(direction.value))
                self.value = 1.0
        elif len(args) == 3:
            value, direction, name = args
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
