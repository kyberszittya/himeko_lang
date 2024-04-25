import time
import typing

from himeko.hbcm.elements.edge import EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from lang.himeko_ast.himeko_ast import Start, extract_root_context, HiNode, HiEdge, AstEnumRelationDirection, create_ast


class AstHbcmTransformer(object):

    def clock_source(self) -> int:
        return time.time_ns()

    def __init__(self):
        self.node_mapping = {}

    def create_hyper_vertex(self, node: HiNode, parent: HyperVertex) -> HyperVertex:
        v = FactoryHypergraphElements.create_vertex_default(str(node.signature.name.value), self.clock_source(), parent)
        self.node_mapping[node] = v
        for n in node.children:
            if isinstance(n, HiNode):
                self.create_hyper_vertex(n, v)
        return v

    def create_edges(self, node: HiNode):
        if isinstance(node, Start):
            for n in node.body.root:
                self.create_edges(n)
        else:
            for n in node.children:
                if isinstance(n, HiNode):
                    self.create_edges(n)
                elif isinstance(n, HiEdge):
                    e = FactoryHypergraphElements.create_edge_default(
                        str(n.signature.name.value), self.clock_source(), self.node_mapping[n.parent])
                    for r in n.relationships:
                        match r.relation_direction:
                            case AstEnumRelationDirection.IN:
                                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.IN, 1.0)
                            case AstEnumRelationDirection.OUT:
                                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.OUT, 1.0)
                            case AstEnumRelationDirection.UNDIRECTED:
                                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.UNDEFINED, 1.0)
                            case AstEnumRelationDirection.UNDEFINED:
                                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.UNDEFINED, 1.0)

    def create_root_hyper_vertices(self, start: Start) -> typing.List[HyperVertex]:
        contexts = []
        for v in extract_root_context(start):
            hv0 = FactoryHypergraphElements.create_vertex_default(v.signature.name.value, self.clock_source())
            for v0 in v.children:
                self.create_hyper_vertex(v0, hv0)
            contexts.append(hv0)
        return contexts

    def convert_tree(self, ast) -> typing.List[HyperVertex]:
        create_ast(ast)
        hyv = self.create_root_hyper_vertices(ast)
        self.create_edges(ast)
        return hyv
