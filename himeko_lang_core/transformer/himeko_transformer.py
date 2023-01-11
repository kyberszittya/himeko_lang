import typing
from datetime import datetime

from lang.himeko_meta_parser import Visitor, Transformer, v_args, Visitor_Recursive, Tree, Token
from lang.identification.strategies import UidIdentificationStrategy, UuidIdentificationStrategy, \
    AbstractIdentificationStrategy
from lang.metaelements.himekoedge import HimekoEdge, RelationDirection
from lang.metaelements.himekoelement import AbstractClock, HimekoConcept
from lang.metaelements.himekonode import HimekoNode

import time

inline_args = v_args(inline=True)

from collections import deque

class SystemTimeClock(AbstractClock):

    def __init__(self):
        super().__init__()

    def tick(self) -> int:
        return time.time_ns()


class HimekoElementFactory(object):

    __HYPERGRAPHNODE_TYPENAME = "himekonode"
    __HYPERGRAPHEDGE_TYPENAME = "himekoedge"

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

    def search_for_string_element(self, t: Tree) -> str:
        r = next(t.find_data("string"))
        return str(r.children[0]).replace("\"","")

    def get_direction(self, direction: str) -> typing.Tuple[RelationDirection, float]:
        match direction:
            case '<-': return RelationDirection.INCOMING, -1.0
            case '--': return RelationDirection.STATIONARY, 0.0
            case '->': return RelationDirection.OUTGOING, 1.0

    def get_direction_from_value(self, value: float) -> typing.Tuple[RelationDirection, float]:
        if value < 0.0:
            return RelationDirection.INCOMING, value
        elif value > 0.0:
            return RelationDirection.OUTGOING, value
        else:
            return RelationDirection.STATIONARY, 0.0


    def get_element_name(self, t: Tree):
        return next(next(filter(
            lambda x: x.data == "hi_element_signature", t.children)).find_data("element_name")).children[0]

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

    def infogenesis(self, t: Tree):
        name = str(self.get_element_name(t))
        genichrone = self.clock.nano_sec
        parent, cnt_cursor_parent = self.get_elem_parent()
        zyg = HimekoConcept(name, parent)
        return name, genichrone, parent, cnt_cursor_parent, zyg

    def generate_himekonode(self, t: Tree):
        name, genichrone, parent, cnt_cursor_parent, zyg = self.infogenesis(t)
        # Generate UID & UUID
        uid = self.f_uid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHNODE_TYPENAME, genichrone)
        uuid = self.f_uuid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHNODE_TYPENAME, genichrone)
        node = HimekoNode(name, uuid, uid, cnt_cursor_parent, parent)
        self.update_elem_parent_fringe(t, parent, node, cnt_cursor_parent)
        self._elements[uuid] = node
        # Add element to parent
        if parent is not None:
            parent.add_children(node)
        # Get parent from queue
        # Check whether this is the root element
        if self._root is None:
            self._root = node
        return node

    def generate_himekoedge(self, t: Tree):
        name, genichrone, parent, cnt_cursor_parent, zyg = self.infogenesis(t)
        uid = self.f_uid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHEDGE_TYPENAME, genichrone)
        uuid = self.f_uuid_id.transform(zyg, HimekoElementFactory.__HYPERGRAPHEDGE_TYPENAME, genichrone)
        edge = HimekoEdge(name, uuid, uid, cnt_cursor_parent, parent)
        self.update_elem_parent_fringe(t, parent, edge, cnt_cursor_parent)
        self._elements[uuid] = edge
        time = self.clock.nano_sec
        for x in filter(lambda x: x.data == "hi_edge_element", t.children):
            if isinstance(x.children[0], Token):
                direction, dir_value = self.get_direction(x.children[0])
            else:
                # TODO: revise for multidimensional data
                for v in x.children[0].find_data("hi_element_value"):
                    direction, dir_value = self.get_direction_from_value(float(v.children[0]))
            ref_name = self.search_for_string_element(next(x.find_data("element_reference"))).split("/")
            referenced_el = edge.search_reference_in_context(ref_name, parent)
            if referenced_el is not None:
                edge.add_connection(referenced_el, ref_name, direction, [dir_value], time)
            else:
                edge.add_uneval_connection(ref_name, direction, [dir_value], time)
        # Add element to parent
        if parent is not None:
            parent.add_children(edge)
        return edge

    @property
    def root(self) -> HimekoNode:
        return self._root


class HypergraphTransformer(Transformer):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphVisitor(Visitor):
    hi_metaelement = lambda self, s: print(s)
    hi_node = lambda self, s: print(s)
    hi_edge = lambda self, s: print(s)


class HypergraphRecursiveVisitor(Visitor_Recursive):

    def __init__(self):
        self._el_factory = HimekoElementFactory()

    hi_metaelement = lambda self, s: None
    hi_node = lambda self, s: self._el_factory.generate_himekonode(s)
    hi_edge = lambda self, s: self._el_factory.generate_himekoedge(s)
    hi_element_field = lambda self, s: print(s)

    @property
    def el_factory(self):
        return self._el_factory

