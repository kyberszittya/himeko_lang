import time
import typing

from himeko.hbcm.elements.edge import EnumRelationDirection, HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from lang.himeko_ast.himeko_ast import Start, extract_root_context, HiNode, HiEdge, AstEnumRelationDirection, \
    create_ast, HiElementField, VectorField, ElementReference


class AstHbcmTransformer(object):

    def clock_source(self) -> int:
        return time.time_ns()

    def __init__(self):
        self.node_mapping = {}
        self.missing_reference = {}

    def create_hyper_vertex(self, node: HiNode, parent: HyperVertex) -> HyperVertex:
        if isinstance(node, HiNode):
            v = FactoryHypergraphElements.create_vertex_default(str(node.signature.name.value), self.clock_source(), parent)
            self.node_mapping[node] = v
            for n in node.children:
                if isinstance(n, HiNode):
                    self.create_hyper_vertex(n, v)
            return v

    def add_relation(self, e: HyperEdge, r):
        val = 1.0
        if r.value is not None:
            val = self.attempt_to_convert_to_float(r)
        match r.relation_direction:
            case AstEnumRelationDirection.IN:
                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.IN, val)
                return e
            case AstEnumRelationDirection.OUT:
                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.OUT, val)
                return e
            case AstEnumRelationDirection.UNDIRECTED:
                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.UNDEFINED, val)
                return e
            case AstEnumRelationDirection.UNDEFINED:
                e += (self.node_mapping[r.reference.reference], EnumRelationDirection.UNDEFINED, val)
                return e
        return e

    def create_edges_node(self, node: HiNode):
        for n in node.children:
            if isinstance(n, HiNode):
                self.create_edges_node(n)
            elif isinstance(n, HiEdge):
                e = FactoryHypergraphElements.create_edge_default(
                    str(n.signature.name.value), self.clock_source(), self.node_mapping[n.parent])
                for r in n.relationships:
                    self.add_relation(e, r)

    def create_edges(self, node: HiNode):
        if isinstance(node, Start):
            for n in node.body.root:
                if isinstance(n, HiNode):
                    self.create_edges_node(n)
        else:
            self.create_edges_node(node)

    @classmethod
    def attempt_to_convert_to_float(cls, arg):
        if isinstance(arg.value, VectorField):
            return [float(x.value) for x in arg.value.value]
        else:
            try:
                return float(arg.value.value)
            except ValueError:
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

    def create_attribute(self, n):
        if isinstance(n, HiElementField):
            value = None
            typ = None
            if n.value is not None and n.type is not None:
                value = self.extract_value(n)
            elif n.value is not None:
                if isinstance(n.value.value, ElementReference):
                    if n.value.value.name in self.node_mapping:
                        value = self.node_mapping[n.value.value.name]
                    else:
                        # TODO: Add to missing reference
                        #self.missing_reference[n] = n.value.value.name
                        print("Not found")
                else:
                    value = self.attempt_to_convert_to_float(n)
            elif n.type is not None:
                typ = str(n.type.type)
            atr = FactoryHypergraphElements.create_attribute_default(
                str(n.name.value),
                value, typ, self.clock_source(), self.node_mapping[n.parent])
            return atr
        else:
            if isinstance(n, HiNode):
                self.create_attributes(n)

    def create_attributes(self, node: HiNode):
        if isinstance(node, Start):
            for n in node.body.root:
                if isinstance(n, HiNode):
                    self.create_attributes(n)
        else:
            if isinstance(node, HiNode):
                for n in node.children:
                    self.create_attribute(n)

    def create_root_hyper_vertices(self, start: Start) -> typing.List[HyperVertex]:
        contexts = []
        for v in extract_root_context(start):
            hv0 = FactoryHypergraphElements.create_vertex_default(v.signature.name.value, self.clock_source())
            self.node_mapping[v] = hv0
            for v0 in v.children:
                self.create_hyper_vertex(v0, hv0)
            contexts.append(hv0)
        return contexts

    def retrieve_references(self):
        found_items = set()
        for k, v in self.missing_reference.items():
            print(v)

    def convert_tree(self, ast) -> typing.List[HyperVertex]:
        create_ast(ast)
        hyv = self.create_root_hyper_vertices(ast)
        self.create_edges(ast)
        self.create_attributes(ast)
        self.retrieve_references()
        return hyv
