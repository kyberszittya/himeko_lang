import typing
from dataclasses import dataclass
import time

from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from lang.himeko_ast.elements.abstract_elements import _HiAbstractElement, HiElementSignature
from lang.himeko_ast.elements.meta_elements import _Ast


@dataclass
class _HiNodeElement(_Ast):
    hi_node_element: _HiAbstractElement

@dataclass
class HiNode(_HiAbstractElement):
    children: typing.List[_HiAbstractElement]
    timestamp: int

    def __init__(self, signature: HiElementSignature, *children):
        super().__init__(signature)
        self.children = list([x.children[0] for x in children])
        self.timestamp = time.time_ns()

    def __hash__(self):
        hashed = [str(self.signature.name.value), self.timestamp]
        hashed.extend([str(c.signature.name.value) for c in
                       filter(lambda x: isinstance(x, HyperVertex) or isinstance(x, HyperEdge), self.children)])
        if self.parent is not None:
            hashed.append(str(self.parent.signature.name.value))
        return hash(tuple(hashed))