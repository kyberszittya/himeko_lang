import time
import typing
from queue import Queue

from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import EnumRelationDirection, HyperEdge, ReferenceQuery
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from lang.himeko_ast.himeko_ast import Start, extract_root_context, HiNode, HiEdge, AstEnumRelationDirection, \
    create_ast, HiElementField, VectorField, ElementReference



class AstElementNotFound(Exception):
    pass


class AstHbcmTransformer(object):

    def clock_source(self) -> int:
        return time.time_ns()

    def __init__(self):
        self.node_mapping = {}
        self.missing_reference = {}
        self.relation_queues = Queue()

    def create_hyper_vertex(self, node: HiNode, parent: HyperVertex) -> HyperVertex:
        if isinstance(node, HiNode):
            v = FactoryHypergraphElements.create_vertex_default(str(node.signature.name.value), self.clock_source(), parent)
            # Check for template
            if node.signature.template is not None:
                node.signature.template.reference.reference = ReferenceQuery(node.signature.template.reference.name)
                self.relation_queues.put((v, node.signature.template.reference.reference, EnumRelationDirection.OUT))
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
                self.relation_queues.put((e, r.reference.reference, EnumRelationDirection.IN, val))
                return e
            case AstEnumRelationDirection.OUT:
                self.relation_queues.put((e, r.reference.reference, EnumRelationDirection.OUT, val))
                return e
            case AstEnumRelationDirection.UNDIRECTED:
                self.relation_queues.put((e, r.reference.reference, EnumRelationDirection.UNDEFINED, val))
                return e
            case AstEnumRelationDirection.UNDEFINED:
                self.relation_queues.put((e, r.reference.reference, EnumRelationDirection.UNDEFINED, val))
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
            return [cls.convert_to_float_value(x) for x in arg.value.value]
        elif isinstance(arg.value, list):
            return [float(x.value) for x in arg.value]
        elif isinstance(arg.value, ElementReference):
            return ReferenceQuery(arg.value.name)
        else:
            return cls.convert_to_float_value(arg)

    @classmethod
    def convert_string(cls, s):
        s = str(s)
        if s.startswith('"') and s.endswith('"'):
            s = s[1:-1]
        if s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
        return s

    @classmethod
    def convert_to_float_value(cls, arg):
        try:
            return float(arg.value)
        except ValueError:
            return cls.convert_string(arg.value)


    @classmethod
    def extract_value(cls, n):
        if isinstance(n.value, VectorField):
            return AstHbcmTransformer.attempt_to_convert_to_float(n)
        else:
            match str(n.type.value.name):
                case "int":
                    return int(n.value.value)
                case "float":
                    return float(n.value.value)
                case "real":
                    return float(n.value.value)
                case "string":
                    return cls.convert_string(n.value.value)
                case "bool":
                    return bool(n.value.value)

    def __create_attribute(self, n: HiElementField):
        value = None
        typ = None
        if n.value is not None and n.type is not None:
            value = self.extract_value(n)
        elif n.value is not None:
            value = self.handle_typed_value(n)
        elif n.type is not None:
            typ = str(n.type.value)
        atr = FactoryHypergraphElements.create_attribute_default(
            str(n.name.value),
            value, typ, self.clock_source(), self.node_mapping[n.parent])
        if isinstance(value, ReferenceQuery):
            self.relation_queues.put((atr, value))
        return atr

    def handle_typed_value(self, n):
        if n.type is not None:
            if isinstance(n.type.value, ElementReference):
                if n.type.value.name in self.node_mapping:
                    value = self.node_mapping[n.type.value.name]
                else:
                    value = ReferenceQuery(n.type.value.name)
            else:
                value = self.attempt_to_convert_to_float(n)
        else:
            value = self.attempt_to_convert_to_float(n.value)
        return value

    def create_attribute(self, n):
        if isinstance(n, HiElementField):
            return self.__create_attribute(n)
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

    def find_element_by_name_fragments(self, element: HyperVertex, fragments: typing.List[str]) -> HyperVertex:
        if len(fragments) == 0:
            return element
        for c in element.get_children(lambda x: x.name == fragments[0], None):
            return self.find_element_by_name_fragments(c, fragments[1:])
        raise AstElementNotFound("Element not found")

    def get_node_references(self, query_split: typing.List[str], element: HyperVertex):
        # Get query root
        root_name = query_split[0]
        root = None
        while element is not None:
            if element.name == root_name:
                root = element
                break
            els = list(element.get_children(lambda x: x.name == root_name, 1))
            if len(els) != 0:
                root = els[0]
                break
            element = element.parent
        if root is None:
            raise AstElementNotFound("Root not found")
        # Get query path
        res = self.find_element_by_name_fragments(root, query_split[1:])
        if res is None:
            raise AstElementNotFound("Element not found")
        return res

    def get_single_node_reference(self, element, query_split):
        fringe = Queue()
        p = element
        # get parent chain
        while p is not None:
            fringe.put(p)
            p = p.parent
        # Get children from single parent relationship
        while not fringe.empty():
            e = fringe.get()
            try:
                res = next(e.get_children(lambda x: x.name == query_split[-1], 1))
                return res
            except StopIteration:
                continue
        return None

    def retrieve_referenced_node(self, e: HyperEdge | HypergraphAttribute, ref):
        query_split = ref.reference_query.split('.')
        element: HyperVertex = e.parent
        if len(query_split) == 1:
            # Ensure that we want to go down to the very parents of the context
            return self.get_single_node_reference(element, query_split)
        else:
            return self.get_node_references(query_split, element)

    def retrieve_references(self, hyv: typing.List[HyperVertex]):
        while not self.relation_queues.empty():
            t = self.relation_queues.get()
            v, r = t[0], t[1]
            v: HyperEdge | HypergraphAttribute
            res = self.retrieve_referenced_node(v, r)
            if res is None:
                for hy in hyv:
                    res = self.get_node_references(r.reference_query.split('.'), hy)
                    if res is not None:
                        break
            if len(t) == 4:
                _, _, d, val = t
                v: HyperEdge
                v += (res, d, val)
            if len(t) == 3:
                v.template = res
            elif len(t) == 2:
                v, r = t
                v: HypergraphAttribute
                v.value = res

    def convert_tree(self, ast) -> typing.List[HyperVertex]:
        create_ast(ast)
        hyv = self.create_root_hyper_vertices(ast)
        self.create_edges(ast)
        self.create_attributes(ast)
        self.retrieve_references(hyv)
        return hyv
