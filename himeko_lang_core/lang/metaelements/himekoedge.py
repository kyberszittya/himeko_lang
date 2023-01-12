import typing
from collections import deque
from enum import Enum

from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement, AbstractHimekoRoot, \
    AbstractHimekoInfoChondrium


class RelationDirection(Enum):
    OUTGOING = 0
    STATIONARY = 1
    INCOMING = 2



class HimekoReference(AbstractHimekoRoot):

    def __init__(self, name: str, target: typing.Optional[AbstractHimekoInfoChondrium],
                 query: str, direction: RelationDirection, value: list[float], genichronos: int = 0):
        super().__init__(name, target, genichronos)
        self._direction = direction
        self._query = query
        self._value = value
        # Connections

    @property
    def query(self):
        return self._query

    @property
    def direction(self):
        return self._direction

    @property
    def value(self):
        return self._value


class HimekoEdge(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        # Store elements
        self._connections = dict()
        # Unevaluated connections
        self._uneval_connections = dict()

    def add_connection(self, target, query: typing.Iterable[str], direction: RelationDirection,
                       value: list[float], timestamp: int):
        ref_name = '/'.join(query)
        name = f"{self.name}-{ref_name}"
        ref = HimekoReference(name, target, ref_name, direction, value, timestamp)
        self._connections[target.uuid] = ref

    def add_uneval_connection(self, query: typing.Iterable[str], direction: RelationDirection,
                              value: list[float], timestamp: int):
        ref_name = '/'.join(query)
        name = f"{self.name}-{ref_name}"
        ref = HimekoReference(name, None, ref_name, direction, value, timestamp)
        self._uneval_connections[ref_name] = ref

    def evaluate_unknown_references(self):
        __matches = deque()
        for e in self._uneval_connections.values():
            ref_name = e.query.split("/")
            ref_el = self.search_reference_in_context(ref_name, self.progenitor)
            if ref_el is not None:
                e.target = ref_el
                __matches.append(e.query)
                self._connections[ref_el.uuid] = e
        for x in __matches:
            self._uneval_connections.pop(x)
