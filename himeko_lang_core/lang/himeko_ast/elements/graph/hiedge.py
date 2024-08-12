import typing
from dataclasses import dataclass

from lang.himeko_ast.elements.abstract_elements import _HiAbstractElement, HiElementSignature
from lang.himeko_ast.elements.graph.elementfield import HiElementField
from lang.himeko_ast.elements.meta_elements import _Ast, AstEnumRelationDirection
from lang.himeko_ast.elements.reference import ElementReference
from lang.himeko_ast.elements.types.data_type import VectorField


@dataclass
class HiEdgeElement(_Ast):
    value: typing.Optional[VectorField]
    relation_direction: AstEnumRelationDirection
    reference: typing.Optional[ElementReference]

    def __init__(self, arg):
        # Check for type of arg (element reference, element field, edge)
        if isinstance(arg, ElementReference):
            self.value = arg.value
            self.relation_direction = arg.direction
            self.reference = arg
        elif isinstance(arg, HiElementField):
            # Todo: add value in a parent relationship
            self.value = arg.value
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None
        elif isinstance(arg, HiEdge):
            # TODO: add edge in a parent relationship
            self.value = arg
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None


@dataclass
class HiEdge(_HiAbstractElement):
    relationships: typing.List[HiEdgeElement]

    def __init__(self, hi_edge_type, signature: HiElementSignature, *vertices: HiEdgeElement):
        super().__init__(signature)
        self.edge_type = hi_edge_type
        self.relationships = list(vertices)
