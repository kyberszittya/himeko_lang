import typing

from himeko_lang.lang.metaelements.himekoedge import HimekoReference, HimekoEdge
from himeko_lang.lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class HimekoNode(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None,
                 primary_template_reference: HimekoReference = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        if primary_template_reference is not None:
            self._primary_template = primary_template_reference
        else:
            self._primary_template = None

    def add_children(self, el: HimekoElement):
        self._elements_by_uid[el.uid] = el

    def evaluate_unknown_references(self):
        for el in self._elements_by_uid.values():
            el.evaluate_unknown_references()

    @property
    def primary_template(self) -> HimekoReference:
        return self._primary_template

    def get_children(self, func: typing.Callable[[typing.Any], bool]):
        return filter(func, self._elements_by_uid.values())

    def get_children_node(self):
        return self.get_children(lambda x: isinstance(x, HimekoNode))

    def get_children_edge(self):
        return self.get_children(lambda x: isinstance(x, HimekoEdge))
