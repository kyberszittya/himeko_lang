import time
import typing

from himeko.hbcm.elements.edge import EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from lang.himeko_ast.himeko_ast import Start, extract_root_context, HiNode, HiEdge, AstEnumRelationDirection, \
    create_ast, HiElementField, VectorField


class AstHbcmTransformer(object):

    def clock_source(self) -> int:
        return time.time_ns()

    def __init__(self):
        self.node_mapping = {}

    def create_hyper_vertex(self, node: HiNode, parent: HyperVertex) -> HyperVertex:
        if isinstance(node, HiNode):
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

    @classmethod
    def attempt_to_convert_to_float(cls, arg):
        if isinstance(arg.value, VectorField):
            return [float(x.value) for x in arg.value.value]
        else:
            try:
                return float(arg.value.value)
            except:
                return str(arg.value.value)

    @classmethod
    def extract_value(cls, n):
        if isinstance(n.value, VectorField):
            return AstHbcmTransformer.attempt_to_convert_to_float(n)
        else:
            match str(n.type.type):
                case "int":
                    return int(n.value.value)
                case "float":
                    return float(n.value.value)
                case "real":
                    return float(n.value.value)
                case "string":
                    return str(n.value.value)
                case "bool":
                    return bool(n.value.value)

    def create_attributes(self, node: HiNode):
        if isinstance(node, Start):
            for n in node.body.root:
                self.create_attributes(n)
        else:
            if isinstance(node, HiNode):
                for n in node.children:
                    if isinstance(n, HiElementField):
                        value = None
                        typ = None
                        if n.value is not None and n.type is not None:
                            value = self.extract_value(n)
                        elif n.value is not None:
                            value = self.attempt_to_convert_to_float(n)
                        elif n.type is not None:
                            typ = str(n.type.type)
                        atr = FactoryHypergraphElements.create_attribute_default(str(n.name.value),
                            value, typ, self.clock_source(), self.node_mapping[n.parent])
                    else:
                        self.create_attributes(n)


    def create_root_hyper_vertices(self, start: Start) -> typing.List[HyperVertex]:
        contexts = []
        for v in extract_root_context(start):
            hv0 = FactoryHypergraphElements.create_vertex_default(v.signature.name.value, self.clock_source())
            self.node_mapping[v] = hv0
            for v0 in v.children:
                self.create_hyper_vertex(v0, hv0)
            contexts.append(hv0)
        return contexts

    def convert_tree(self, ast) -> typing.List[HyperVertex]:
        create_ast(ast)
        hyv = self.create_root_hyper_vertices(ast)
        self.create_edges(ast)
        self.create_attributes(ast)
        return hyv
