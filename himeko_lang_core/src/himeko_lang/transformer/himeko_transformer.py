import typing

from himeko.common.clock import SystemTimeClock
from himeko_lang.lang.himeko_meta_parser import Visitor, Transformer, v_args, Visitor_Recursive, Tree, Token
from himeko_lang.lang.identification.strategies import UidIdentificationStrategy, UuidIdentificationStrategy, \
    AbstractIdentificationStrategy
from himeko_lang.lang.metaelements.himekoedge import HimekoEdge, RelationDirection, HimekoReference
from himeko_lang.lang.metaelements.himekoelement import HimekoConcept, HimekoElement
from himeko_lang.lang.metaelements.himekonode import HimekoNode


from himeko_lang.lang.metaelements.himekovalue import HimekoValue

inline_args = v_args(inline=True)

from collections import deque





class HimekoElementFactory(object):

    __HYPERGRAPHNODE_TYPENAME = "himekonode"
    __HYPERGRAPHEDGE_TYPENAME = "himekoedge"
    __HYPERGRAPHVALUE_TYPENAME = "himekovalue"

    def __init__(self, clock=None):
        self.f_uid_id: AbstractIdentificationStrategy = UidIdentificationStrategy()
        self.f_uuid_id: AbstractIdentificationStrategy = UuidIdentificationStrategy()
        # Clock
        if clock is None:
            self.clock = SystemTimeClock()
        # Node root
        self._root = None
        # All nodes
        self._elements = {}
        # Current context
        self.fringe = deque()

    def generate_reference(self, name, query, target, direction, value, timestamp: int):
        ref_name = '/'.join(query)
        name = f"{name}-{ref_name}"
        ref = HimekoReference(name, target, ref_name, direction, value, timestamp)
        return ref



    def get_direction(self, direction: str) -> typing.Tuple[RelationDirection, float]:
        match direction:
            case '<-': return RelationDirection.INCOMING, -1.0
            case '--': return RelationDirection.BIDIRECTIONAL, 1.0
            case '->': return RelationDirection.OUTGOING, 1.0

    def get_direction_from_value(self, value: float) -> typing.Tuple[RelationDirection, float]:
        if value < 0.0:
            return RelationDirection.INCOMING, value
        elif value > 0.0:
            return RelationDirection.OUTGOING, value
        else:
            return RelationDirection.BIDIRECTIONAL, value




    def get_elem_parent(self):
        if len(self.fringe) > 0:
            return self.fringe.pop()
        else:
            return None, 0

    def update_elem_parent_fringe(self, t: Tree, parent, node, cnt_cursor_parent):
        # Update parent relationship
        cnt_children = len(list(filter(lambda x: x.data == "hi_element", t.children)))
        if cnt_cursor_parent - 1 > 0 and parent is not None:
            self.fringe.append((parent, cnt_cursor_parent - 1))
        if cnt_children != 0:
            self.fringe.append((node, cnt_children))

    def infogenesis(self, t: Tree) -> typing.Tuple[str, int, typing.Optional[HimekoNode], int, HimekoConcept]:
        name = str(self.get_element_name(t))
        genichrone = self.clock.nano_sec
        parent, cnt_cursor_parent = self.get_elem_parent()
        zyg = HimekoConcept(name, parent)
        return name, genichrone, parent, cnt_cursor_parent, zyg

    def _get_template(self, t: Tree, progenitor, genichronos: int):
        _sig = list(filter(lambda x: x.data == "hi_element_signature", t.children))[0]
        # Get template
        _templ_el = list(filter(lambda x: x.data == "hi_templating", _sig.children))
        if len(_templ_el) > 0:
            query = _templ_el[0]
            ref_name, _templ = self.get_reference(query, progenitor, None)
            template_conn = HimekoReference(f"templ_{ref_name}", _templ, query, RelationDirection.OUTGOING, [1.0], genichronos)
            return template_conn

        return None

    def generate_himekonode(self, t: Tree):
        name, genichrone, progenitor, cnt_cursor_parent, zyg = self.infogenesis(t)
        # Generate UID & UUID
        uid = self.f_uid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHNODE_TYPENAME, genichrone)
        uuid = self.f_uuid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHNODE_TYPENAME, genichrone)
        # Template
        _templ = self._get_template(t, progenitor, genichrone)
        # Create node
        if _templ is not None:
            node = HimekoNode(name, uuid, uid, cnt_cursor_parent, progenitor, _templ)
        else:
            node = HimekoNode(name, uuid, uid, cnt_cursor_parent, progenitor)
        self.update_elem_parent_fringe(t, progenitor, node, cnt_cursor_parent)
        self._elements[uuid] = node
        # Add element to parent
        if progenitor is not None:
            progenitor.add_children(node)
        # Get parent from queue
        # Check whether this is the root element
        if self._root is None:
            self._root = node
        return node

    def get_reference(self, x: Tree, progenitor, el: typing.Optional[HimekoElement]):
        if el is not None:
            ref_name = self.search_for_string_element(next(x.find_data("element_reference"))).split("/")
            referenced_el = el.search_reference_in_context(ref_name, progenitor)
            return ref_name, referenced_el
        else:
            ref_name = self.search_for_string_element(next(x.find_data("element_reference"))).split("/")
            referenced_el = progenitor.search_reference_in_context(ref_name, progenitor)
            return ref_name, referenced_el

    def generate_himekoedge(self, t: Tree):
        name, genichrone, progenitor, cnt_cursor_parent, zyg = self.infogenesis(t)
        uid = self.f_uid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHEDGE_TYPENAME, genichrone)
        uuid = self.f_uuid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHEDGE_TYPENAME, genichrone)
        edge = HimekoEdge(name, uuid, uid, cnt_cursor_parent, progenitor)
        self.update_elem_parent_fringe(t, progenitor, edge, cnt_cursor_parent)
        self._elements[uuid] = edge
        for x in filter(lambda x: x.data == "hi_edge_element", t.children):
            if isinstance(x.children[0], Token):
                direction, dir_value = self.get_direction(x.children[0])
            else:
                # TODO: revise for multidimensional data
                for v in x.children[0].find_data("hi_element_value"):
                    direction, dir_value = self.get_direction_from_value(float(v.children[0]))
            ref_name, referenced_el = self.get_reference(x, progenitor, edge)
            edge.add_connection(referenced_el, ref_name, direction, dir_value, genichrone)
        # Add element to parent
        if progenitor is not None:
            progenitor.add_children(edge)
        return edge

    def generate_himekovalue(self, t: Tree):
        name, genichrone, progenitor, cnt_cursor_parent, zyg = self.infogenesis(t)
        uid = self.f_uid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHVALUE_TYPENAME, genichrone)
        uuid = self.f_uuid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHVALUE_TYPENAME, genichrone)
        value = HimekoValue(name, uuid, uid, cnt_cursor_parent, progenitor)
        self.update_elem_parent_fringe(t, progenitor, value, cnt_cursor_parent)
        self._elements[uuid] = value
        # Try getting values
        try:
            vt = next(t.find_data("hi_element_value"))
            if not isinstance(vt.children[0], Token):
                if vt.children[0].data == "element_reference":
                    ref_name, referenced_el = self.get_reference(vt, progenitor, value)
                    v = self.generate_reference(name, ref_name, referenced_el, RelationDirection.OUTGOING, 1.0, genichrone)
                else:
                    v = str(vt.children[0].children[0])
            else:
                v = str(vt.children[0])
        except StopIteration:
            v = None
        # Try parsing values
        try:
            el_type = next(t.find_data("element_type"))
            value.value_type = el_type.children[0]
            # Value
            if v is not None:
                match el_type.children[0]:
                    case "string":
                        value.value = str(v).replace('"',"")
                    case "real":
                        value.value = float(v)
                    case "int":
                        value.value = int(v)
        except StopIteration:
            # Assignment of variable
            if v is not None and isinstance(v, str):
                value.value = v.replace('"', "")
            else:
                value.value = v
        # Add element to parent
        if progenitor is not None:
            progenitor.add_children(value)
        return value

    @property
    def root(self) -> HimekoNode:
        return self._root


class HypergraphTransformer(Transformer):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphVisitor(Visitor):
    def hi_node(self, s):
        print("Node: "+ str(s))

    def hi_element_signature(self, s):
        print(s)
        print(s.children)


class HypergraphRecursiveVisitor(Visitor_Recursive):

    def __init__(self):
        self._el_factory = HimekoElementFactory()

    hi_metaelement = lambda self, s: None
    hi_node = lambda self, s: self._el_factory.generate_himekonode(s)
    hi_edge = lambda self, s: self._el_factory.generate_himekoedge(s)
    hi_element_field = lambda self, s: self._el_factory.generate_himekovalue(s)

    @property
    def el_factory(self):
        return self._el_factory

