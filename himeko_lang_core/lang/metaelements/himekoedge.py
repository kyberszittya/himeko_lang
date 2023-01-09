from enum import Enum

from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement, AbstractHimekoRoot, \
    AbstractHimekoInfoChondrium


class RelationDirection(Enum):
    OUTGOING = 0
    BIDIRECTIONAL = 1
    INCOMING = 2



class HimekoReference(AbstractHimekoRoot):

    def __init__(self, name: str, target: AbstractHimekoInfoChondrium,
                 direction: RelationDirection, genichronos: int = 0):
        super().__init__(name, target, genichronos)
        self.direction = direction
        # Connections


class HimekoEdge(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        # Store elements
        self._elements_by_cid = {}
        self._elements_by_uid = {}
        self._connections = dict()

    def add_connection(self, target, direction: RelationDirection, time: int):
        name = f"{self.name}-{target.name}"
        ref = HimekoReference(name, target, direction, time)
        self._connections[target.uuid] = ref


