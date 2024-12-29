import typing
from collections import deque
from enum import Enum

from himeko_lang.lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement, \
    AbstractHimekoInfoChondrium, AbstractHimekoRoot


class RelationDirection(Enum):
    OUTGOING = 0
    BIDIRECTIONAL = 1
    INCOMING = 2



class HimekoReference(AbstractHimekoRoot):

    def __init__(self, name: str, target: typing.Optional[AbstractHimekoInfoChondrium],
                 query: str, direction: RelationDirection, value: list[float], genichronos: int = 0):
        super().__init__(name, target, genichronos)
        self._direction = direction
        self._query = query
        self._value = value
        # Connections
        self._eval_element = False

    # Reference query
    @property
    def query(self):
        return self._query

    # Direction value
    @property
    def direction(self):
        return self._direction

    @property
    def value(self):
        return self._value

    # Evaluated reference element
    @property
    def eval_element(self):
        return self._eval_element

    @eval_element.setter
    def eval_element(self, val):
        self._eval_element = val


class HimekoEdge(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        # Store elements
        self._eval_connections = dict()
        # Unevaluated connections
        self._uneval_connections = dict()

    def add_eval_connection(self, target, query: typing.Iterable[str], direction: RelationDirection,
                       value: list[float], timestamp: int):
        ref_name = '/'.join(query)
        name = f"{self.name}-{ref_name}"
        ref = HimekoReference(name, target, ref_name, direction, value, timestamp)
        self._eval_connections[target.uuid] = ref

    def add_uneval_connection(self, query: typing.Iterable[str], direction: RelationDirection,
                              value: list[float], timestamp: int):
        ref_name = '/'.join(query)
        name = f"{self.name}-{ref_name}"
        ref = HimekoReference(name, None, ref_name, direction, value, timestamp)
        self._uneval_connections[ref_name] = ref

    def add_connection(self, referenced_el, ref_name, direction, dir_value, genichrone):
        if referenced_el is not None:
            self.add_eval_connection(referenced_el, ref_name, direction, [dir_value], genichrone)
        else:
            self.add_uneval_connection(ref_name, direction, [dir_value], genichrone)

    def evaluate_unknown_references(self):
        __matches = deque()
        for e in self._uneval_connections.values():
            ref_name = e.query.split("/")
            ref_el = self.search_reference_in_context(ref_name, self.progenitor)
            if ref_el is not None:
                e.target = ref_el
                __matches.append(e.query)
                e.eval_element = True
                self._eval_connections[ref_el.uuid] = e
        for x in __matches:
            self._uneval_connections.pop(x)

    def get_target_uuids(self):
        return set([x.target.uuid for x in self._eval_connections.values()])

    def outgoing_targets(self):
        return ([(x.target.uuid, x.value, x.direction) for x in self._eval_connections.values()
                     if x.value[0] > 0.0 or x.direction==RelationDirection.OUTGOING or x.direction==RelationDirection.BIDIRECTIONAL])

    def incoming_targets(self):
        return ([(x.target.uuid, x.value, x.direction) for x in self._eval_connections.values()
                     if x.value[0] < 0.0 or x.direction==RelationDirection.INCOMING or x.direction==RelationDirection.BIDIRECTIONAL])
