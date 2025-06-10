from dataclasses import dataclass


from himeko_lang.lang.himeko_ast.elements.meta_elements import AstEnumRelationDirection, _Ast, enumerate_direction, \
    enumerate_modifier, AstEnumRefereneModifier
from himeko_lang.lang.himeko_ast.elements.types.data_type import VectorField


@dataclass
class ElementReference(_Ast):
    name: str
    modif: AstEnumRefereneModifier

    def __init__(self, *args):
        if len(args) == 1:
            self.direction = None
            self.name = args[0].replace('"', '')
            self.direction = AstEnumRelationDirection.UNDEFINED
            self.value = 1.0
            self.modif = AstEnumRefereneModifier.USE
        elif len(args) == 2:
            direction, name = args
            self.name = name.replace('"', '')
            # Check if we have a value instead of direction
            if isinstance(direction, VectorField):
                self.direction = AstEnumRelationDirection.UNDEFINED
                self.value = direction
            else:
                # Else a simple relation is defined
                self.direction = direction.direction
                self.value = 1.0
            self.modif = AstEnumRefereneModifier.USE
        elif len(args) == 3:
            if not isinstance(args[0], VectorField) and (args[0].type == "REFERENCE_MODIFIER"):
                modif, direction, name = args
                self.direction = enumerate_direction(str(direction.value))
                self.name = name.replace('"', '')
                self.modif = enumerate_modifier(str(modif.value))
                self.value = 1.0
            else:
                value, direction, name = args
                self.direction = enumerate_direction(str(direction.value))
                self.name = name.replace('"', '')
                self.value = value
        elif len(args) == 4:
            value, modif, direction, name = args
            self.direction = enumerate_direction(str(direction.value))
            self.name = name.replace('"', '')
            self.value = value
            self.modif = modif

        self._reference = None

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value
