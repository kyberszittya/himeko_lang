import os
import typing
import logging
from copy import copy
from dataclasses import dataclass
from queue import Queue, PriorityQueue


from himeko.common.clock import AbstractClock, SystemTimeClock
from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import EnumHyperarcDirection, HyperEdge, ReferenceQuery, EnumHyperarcModifier
from himeko.hbcm.elements.element import HypergraphElement
from himeko.hbcm.elements.vertex import HyperVertex, Metadata
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko_lang.lang.himeko_ast.elements.graph.elementfield import HiElementField
from himeko_lang.lang.himeko_ast.elements.graph.hiedge import HiEdge, EdgeElementType, HiEdgeElement
from himeko_lang.lang.himeko_ast.elements.graph.hinode import HiNode
from himeko_lang.lang.himeko_ast.elements.meta_elements import AstEnumRelationDirection, AstEnumRefereneModifier
from himeko_lang.lang.himeko_ast.elements.reference import ElementReference
from himeko_lang.lang.himeko_ast.elements.types.data_type import VectorField, HiElementValue
from himeko_lang.lang.himeko_ast.himeko_ast import Start, extract_root_context, \
    create_ast, extract_meta_context, HiMeta
from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone
from himeko_lang.lang.himeko_ast.himeko_ast import transformer


class AstElementNotFound(Exception):
    pass


class AstGraphPathNotFound(Exception):
    pass

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task: typing.Any


class AstHbcmTransformer(object):

    def clock_source(self) -> int:
        return self.clock_source.tick()

    def __init__(self, clock_source: typing.Optional[AbstractClock] = None):
        self.element_mapping = {}
        self.missing_reference = {}
        self.relation_queues = Queue()
        # Copy and other operations
        self.operation_queues = PriorityQueue()
        # Usage mapping
        self.reference_mapping = {}
        # Define clock source
        if clock_source is not None:
            self.clock_source = clock_source
        else:
            self.clock_source = SystemTimeClock()
        # Meta elements storage
        self.meta_elements = {}
        # Logging
        self.logger = logging.getLogger(__name__)

    def setup_stereotype(self, ast_element: HiNode | HiEdge, element: HypergraphElement):
        # Check for stereotype
        if ast_element.signature.template is not None:
            ast_element.signature.template.reference.reference = ReferenceQuery(
                ast_element.signature.template.reference.name)
            self.relation_queues.put((
                element, ast_element.signature.template.reference.reference,
                EnumHyperarcDirection.OUT, 1.0, ast_element.signature.template.reference.modif)
            )

    def __create_hyper_node(self, node: HiNode, parent: typing.Optional[HyperVertex]) -> HyperVertex:
        if parent is None:
            v = FactoryHypergraphElements.create_vertex_default(
                str(node.signature.name.value), self.clock_source.tick())
        else:
            v = FactoryHypergraphElements.create_vertex_default(
                str(node.signature.name.value), self.clock_source.tick(), parent)
        # Get usages
        if len(node.signature.usage) > 0:
            self.reference_mapping[v] = [x.reference.name for x in node.signature.usage]
        # Setup stereotypes
        self.setup_stereotype(node, v)
        # Add to self node mapping
        self.element_mapping[node] = v
        for n in node.children:
            if isinstance(n, HiNode):
                self.create_hyper_vertex(n, v)
        return v

    def create_hyper_vertex(self, node: HiNode, parent: HyperVertex) -> HyperVertex:
        if isinstance(node, HiNode):
            return self.__create_hyper_node(node, parent)

    def add_relation(self, e: HyperEdge, r):
        val = 1.0
        if r.element is not None:
            val = self.attempt_to_convert_to_float(r)
        match r.relation_direction:
            case AstEnumRelationDirection.IN:
                self.relation_queues.put(
                    (e, r.reference.reference, EnumHyperarcDirection.IN, val))
                return e
            case AstEnumRelationDirection.OUT:
                self.relation_queues.put(
                    (e, r.reference.reference, EnumHyperarcDirection.OUT, val))
                return e
            case AstEnumRelationDirection.UNDIRECTED:
                self.relation_queues.put(
                    (e, r.reference.reference, EnumHyperarcDirection.UNDEFINED, val))
                return e
            case AstEnumRelationDirection.UNDEFINED:
                self.relation_queues.put(
                    (e, r.reference.reference, EnumHyperarcDirection.UNDEFINED, val))
                return e
        return e

    def create_edge(self, edge: HiEdge):
        e = FactoryHypergraphElements.create_edge_default(
            str(edge.signature.name.value),
            self.clock_source.tick(),
            self.element_mapping[edge.parent]
        )
        # Get usages
        if len(edge.signature.usage) > 0:
            self.reference_mapping[e] = [x.reference.name for x in edge.signature.usage]
        # Setup stereotypes
        self.setup_stereotype(edge, e)
        # Add to self node mapping
        self.element_mapping[edge] = e
        # Add relations
        for r in filter(lambda x: x.element_type == EdgeElementType.RELATIONSHIP, edge.children):
            self.add_relation(e, r)
        # Add edges
        for r in filter(lambda x: x.element_type == EdgeElementType.EDGE, edge.children):
            self.create_edge(r.element)

    def create_edges_node(self, node: HiNode | HiEdge):
        for n in node.children:
            if isinstance(n, HiNode):
                self.create_edges_node(n)
            elif isinstance(n, HiEdge):
                self.create_edge(n)

    def create_edges(self, node: HiNode):
        if isinstance(node, Start):
            for n in node.body.root:
                if isinstance(n, HiNode):
                    self.create_edges_node(n)
        else:
            self.create_edges_node(node)

    @classmethod
    def attempt_to_convert_to_float(cls, arg):
        if isinstance(arg, HiEdgeElement):
            if (isinstance(arg.element, VectorField) or
                    isinstance(arg.element, HiElementField)):
                return cls.attempt_to_convert_to_float(arg.element)
            else:
                return cls.convert_to_float_value(arg.element)
        else:
            if isinstance(arg, VectorField):
                return [cls.convert_to_float_value(x) for x in arg.value]
            elif isinstance(arg, list):
                return [float(x.value) for x in arg]
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
            if isinstance(arg, HiElementValue):
                return cls.convert_to_float_value(arg.value)
            elif isinstance(arg, VectorField):
                return [cls.convert_to_float_value(x) for x in arg.value]
            elif isinstance(arg, ElementReference):
                match arg.modif:
                    case AstEnumRefereneModifier.COPY:
                        return ReferenceQuery(arg.name, EnumHyperarcModifier.COPY)

            return float(arg)
        except ValueError:
            return cls.convert_string(arg)


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
            value, typ, self.clock_source.tick(), self.element_mapping[n.parent])
        if isinstance(value, ReferenceQuery):
            self.relation_queues.put((atr, value))
        return atr

    def handle_typed_value(self, n):
        if n.type is not None:
            if isinstance(n.type.value, ElementReference):
                if n.type.value.name in self.element_mapping:
                    value = self.element_mapping[n.type.value.name]
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
            if isinstance(n, HiNode) or isinstance(n, HiEdge):
                self.create_attributes(n)

    def create_attributes(self, node: HiNode | HiEdge):
        if isinstance(node, Start):
            for n in node.body.root:
                if isinstance(n, HiNode):
                    self.create_attributes(n)
        else:
            if isinstance(node, HiNode):
                for n in node.children:
                    self.create_attribute(n)
            if isinstance(node, HiEdge):
                for n in node.children:
                    if isinstance(n.element, HiElementField):
                        self.create_attribute(n.element)


    def create_root_hyper_vertices(self, start: Start) -> typing.List[HyperVertex]:
        contexts = []
        for v in extract_root_context(start):
            hv0 = self.__create_hyper_node(v, None)
            contexts.append(hv0)
        return contexts

    def get_importable_graphs(self, ast):
        return [_meta.value for _meta in extract_meta_context(ast).includes]

    def find_element_by_name_fragments(self, element: HypergraphElement, fragments: typing.List[str]) -> HypergraphElement:
        if len(fragments) == 0:
            return element
        for c in element.get_children(lambda x: x.name == fragments[0], None):
            return self.find_element_by_name_fragments(c, fragments[1:])
        raise AstElementNotFound(f"Element not found: {fragments}")

    def \
            get_element_references(self,
                               query_split: typing.List[str],
                               element: HypergraphElement):
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
        # If root is not found then return None
        if root is None:
            return None
        # Get query path
        res = self.find_element_by_name_fragments(root, query_split[1:])

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

    def retrieve_referenced_element(self, e: HyperEdge | HypergraphAttribute, ref):
        query_split = ref.reference_query.split('.')
        element: HypergraphElement = e.parent
        if len(query_split) == 1:
            # Ensure that we want to go down to the very parents of the context
            return self.get_single_node_reference(element, query_split)
        else:
            return self.get_element_references(query_split, element)

    def __init_query_elements(self, hyv):
        # Copy the query elements from the main context
        query_elements = [e for e in hyv]
        # Get all usage in context graphs
        for h in hyv:
            if h in self.reference_mapping:
                query_elements.extend(self.reference_mapping[h])
        return query_elements

    def __copy_vertices(self, root: HypergraphElement, template: HypergraphElement):
        root_name = root.name
        __mapping_guid = {template.guid: root}
        for c in template.get_all_children(lambda x: not isinstance(x, HyperEdge)):
            element_name = '_'.join([root_name, c.name])
            el = None
            if isinstance(c, HyperVertex):
                el = FactoryHypergraphElements.create_vertex_default(
                    element_name,
                    self.clock_source.tick(), __mapping_guid[c.parent.guid])
                el.add_stereotype(c)
            elif isinstance(c, HypergraphAttribute):
                if c.name not in root:
                    el = FactoryHypergraphElements.create_attribute_default(
                        c.name,
                        c.value, c.type, self.clock_source.tick(),
                        __mapping_guid[c.parent.guid])
                    el.value = copy(c.value)
            else:
                raise ValueError(f"Unable to copy element of type {type(c)}")
            # If the element is anyhow not initialized, don't add to the mapping dictionary
            if el is not None:
                __mapping_guid[c.guid] = el
        # Edge copy
        for c in template.get_all_children(lambda x: isinstance(x, HyperEdge)):
            element_name = '_'.join([root_name, c.name])
            e = FactoryHypergraphElements.create_edge_default(
                element_name,
                self.clock_source.tick(), __mapping_guid[c.parent.guid])
            for r in c.all_relations():
                if r.target.guid in __mapping_guid:
                    t = (__mapping_guid[r.target.guid], r.direction, copy(r.value))
                else:
                    t = (r.target, r.direction, copy(r.value))
                e += t
            e.add_stereotype(c)

    def retrieve_references(self, hyv: typing.List[HyperVertex]):
        query_elements = self.__init_query_elements(hyv)
        # Process all relations
        while not self.relation_queues.empty():
            t = self.relation_queues.get()
            v, r = t[0], t[1]
            v: HyperEdge | HypergraphAttribute
            res = self.retrieve_referenced_element(v, r)
            # Check whether node is in usage mapping
            if v in self.reference_mapping:
                query_elements.extend(self.reference_mapping[r])
            # Retry query
            if res is None:
                for hy in query_elements:
                    res = self.get_element_references(r.reference_query.split('.'), hy)
                    if res is not None:
                        break
            # Check if there is no result
            if res is None:
                raise AstElementNotFound(f"Element not found: {r.reference_query}")
            # Check tuples by length
            # Check if we are dealing with an edge
            if len(t) == 2:
                v, r = t
                v: HypergraphAttribute
                v.value = res
            elif len(t) == 3:
                v.stereotype = res
            elif len(t) == 4:
                _, _, d, val = t
                if isinstance(val, list):
                    new_val = []
                    for ref_val in val:
                        if isinstance(ref_val, ReferenceQuery):
                            folded = self.retrieve_referenced_element(v, ref_val)
                            match ref_val.modifier:
                                case EnumHyperarcModifier.COPY:
                                    new_val.append(copy(folded.value))
                                case EnumHyperarcModifier.USE:
                                    new_val.append(folded)
                        else:
                            new_val.append(ref_val)
                    if len(new_val) == 1:
                        new_val = new_val[0]
                    val = new_val
                v: HyperEdge
                v += (res, d, val)
            elif len(t) == 5:
                v.stereotype = res
                match t[4]:
                    case AstEnumRefereneModifier.COPY:
                        prio = len(v.stereotype.nameset)
                        task = PrioritizedTask(prio, (v, res, "copy"))
                        self.operation_queues.put(task)

    def max_stereotype(self, v: HypergraphElement):
        prio = len(v.stereotype.nameset)
        for el in  v.get_all_children(lambda x: True):
            prio = max(prio, self.max_stereotype(el))
        return prio

    def read_graph(self, path: str):
        # Transformer
        parser = Lark_StandAlone(transformer=transformer)
        # Read file
        if os.path.exists(path):
            with open(path) as f:
                tree = parser.parse(f.read())
        if tree is None:
            raise AstGraphPathNotFound(f"Unable to read tree from path {path}")
        return tree

    def __import_graphs(self, hyv: typing.List, ast, path: typing.Optional[str|typing.List[str]] = None):
        # Check if includes are present
        meta = extract_meta_context(ast)
        if meta is not None and hasattr(meta, 'includes'):
            import_graphs = self.get_importable_graphs(ast)
            if len(import_graphs) > 0:
                for import_graph in import_graphs:
                    if path is not None:
                        if isinstance(path, list):
                            # Iterate over paths
                            for p in path:
                                # Check if the file exists in the folder
                                if os.path.exists(os.path.join(p, import_graph)):
                                    import_graph = os.path.join(p, import_graph)
                                    break
                        else:
                            if not os.path.exists(os.path.join(path, import_graph)):
                                raise AstGraphPathNotFound("Unable to read tree from path {}".format(import_graph))
                            import_graph = os.path.join(path, import_graph)
                    self.logger.info("Importing graph: {}".format(import_graph))
                    if import_graph in self.meta_elements:
                        import_ast = self.meta_elements[import_graph]


                    else:
                        import_ast = self.read_graph(import_graph)
                        create_ast(import_ast)
                        meta_elements = self.create_root_hyper_vertices(import_ast)
                    # Extend hyper vertices
                    hyv.extend(meta_elements)
                    # Create edge
                    self.create_edges(import_ast)
                    # Create attributes
                    self.create_attributes(import_ast)
                hyv = hyv[::-1]

                return hyv
        return hyv

    def __update_used_elements(self, k, h, used_elements: typing.List):
        for u in self.reference_mapping[k]:
            __retr = h.query_subelements(u)
            if __retr is not None:
                used_elements.append(__retr)
            else:
                __retr = list(h.get_subelements(lambda x: x.name == u, None, True))
                if len(__retr) > 0:
                    used_elements.extend(__retr)
        return used_elements

    def __init_reference_mapping(self, hyv):
        new_reference_mapping = {}
        for k in self.reference_mapping:
            used_elements = []
            for h in hyv:
                used_elements = self.__update_used_elements(k, h, used_elements)
                new_reference_mapping[k] = used_elements
        self.reference_mapping = new_reference_mapping

    def __execute_operations(self):
        # Reprioritize operations
        operations = PriorityQueue()
        while not self.operation_queues.empty():
            t = self.operation_queues.get().task
            prio = len(t[0].stereotype.nameset)
            prio = prio + self.max_stereotype(t[1])
            operations.put(PrioritizedTask(prio, t))
        # Execute operations
        while not operations.empty():
            t = operations.get().task
            v, res, op = t
            if op == "copy":
                self.__copy_vertices(v, res)

    def convert_tree(self, ast, path=None) -> typing.List[HyperVertex]:
        create_ast(ast)
        hyv = self.create_root_hyper_vertices(ast)
        # Import graphs
        hyv = self.__import_graphs(hyv, ast, path)
        # Create meta for root element
        meta = Metadata(str(ast.meta.name.value))
        # Add metaelement to meta
        for m in ast.meta.meta:
            # TODO: finish key value pairs
            print(m)
            meta.add_metaelement(m)
        # Add includes to meta
        for m in ast.meta.includes:
            meta.add_import(m.value)
        hyv[-1].add_meta(meta)
        # Create root node
        # Create edges
        self.create_edges(ast)
        # Create attributes
        self.create_attributes(ast)
        # Collect all usage references for all elements
        self.__init_reference_mapping(hyv)
        # Retrieve references
        self.retrieve_references(hyv)
        # Execute operations
        self.__execute_operations()
        return hyv

