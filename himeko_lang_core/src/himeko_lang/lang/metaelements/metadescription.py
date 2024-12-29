from himeko_lang.lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class MetaDescription(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)