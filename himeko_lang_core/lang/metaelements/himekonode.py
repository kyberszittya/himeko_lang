import abc

from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class HimekoNode(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        # Store nodes
        # TODO: use some more sophisticated method
        self._nodes_by_cid = {}
        self._nodes_by_uid = {}
        # Store edges
        self._edges_by_cid = {}
        self._edges_by_uid = {}


