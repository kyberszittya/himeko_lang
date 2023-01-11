from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class HimekoNode(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)

    def add_children(self, el: HimekoElement):
        self._elements_by_uid[el.uid] = el


