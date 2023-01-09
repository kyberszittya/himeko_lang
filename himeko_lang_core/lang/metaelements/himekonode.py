import abc

from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class HimekoNode(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        # Store elements
        self._elements_by_cid = {}
        self._elements_by_uid = {}

    def add_children(self, el: HimekoElement):
        self._elements_by_uid[el.uid] = el

    def get_node_by_name(self, name: str):
        return filter(lambda x: x.name == name, self._elements_by_uid.values())
