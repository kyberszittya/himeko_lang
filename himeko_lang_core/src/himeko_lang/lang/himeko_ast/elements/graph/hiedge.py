import time
import typing
from dataclasses import dataclass
from enum import Enum

from himeko.hbcm.elements.edge import HyperEdge, ReferenceQuery
from himeko.hbcm.elements.vertex import HyperVertex
from himeko_lang.lang.himeko_ast.elements.abstract_elements import _HiAbstractElement, HiElementSignature
from himeko_lang.lang.himeko_ast.elements.graph.elementfield import HiElementField
from himeko_lang.lang.himeko_ast.elements.meta_elements import _Ast, AstEnumRelationDirection
from himeko_lang.lang.himeko_ast.elements.reference import ElementReference
from himeko_lang.lang.himeko_ast.elements.types.data_type import VectorField

class EdgeElementType(Enum):
    RELATIONSHIP = 0
    EDGE = 1
    VALUE = 2

@dataclass
class HiEdgeElement(_Ast):
    element: typing.Optional[VectorField|HiElementField|_HiAbstractElement]
    relation_direction: AstEnumRelationDirection
    reference: typing.Optional[ElementReference]
    element_type: EdgeElementType

    def __init__(self, arg):
        # Check for type of arg (element reference, element field, edge)
        if isinstance(arg, ElementReference):
            self.element = arg.value
            self.relation_direction = arg.direction
            self.reference = arg
            self.element_type = EdgeElementType.RELATIONSHIP
        elif isinstance(arg, HiElementField):
            self.element = arg
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None
            self.element_type = EdgeElementType.VALUE
        elif isinstance(arg, HiEdge):
            self.element = arg
            self.relation_direction = AstEnumRelationDirection.UNDEFINED
            self.reference = None
            self.element_type = EdgeElementType.EDGE


@dataclass
class HiEdge(_HiAbstractElement):
    children: typing.List[HiEdgeElement]
    timestamp: int

    def __init__(self, hi_edge_type, signature: HiElementSignature, *elements: HiEdgeElement):
        super().__init__(signature)
        self.edge_type = hi_edge_type
        self.children = list(elements)
        self.timestamp = time.time_ns()

    def __hash__(self):
        hashed = [str(self.signature.name.value), self.timestamp]
        hashed.extend([str(c.signature.name.value) for c in
                       filter(lambda x: isinstance(x, HyperVertex) or isinstance(x, HyperEdge), self.children)])
        if self.parent is not None:
            hashed.append(str(self.parent.signature.name.value))
        return hash(tuple(hashed))


def convert_references(edge: HiEdge):
    # First convert references in children (leafs)
    for v in filter(lambda x: x.reference is not None, edge.children):
        v.reference.reference = ReferenceQuery(v.reference.name)
    # Then convert references in edges
    for v in filter(lambda x: x.element_type == EdgeElementType.EDGE, edge.children):
        convert_references(v.element)
