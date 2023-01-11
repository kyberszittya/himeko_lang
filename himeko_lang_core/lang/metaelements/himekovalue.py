from lang.metaelements.himekoelement import HimekoElement, AbstractHimekoElement


class HimekoValue(HimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0, progenitor: AbstractHimekoElement = None):
        super().__init__(name, uuid, uid, cid, progenitor)
        self._value = None
        self._value_type = None
        self._is_assigned = False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val is None:
            self._is_assigned = False
        else:
            self._is_assigned = True
        self._value = val

    @property
    def value_type(self):
        return self._value_type

    @value_type.setter
    def value_type(self, v):
        self._value_type = v

    @property
    def is_assigned(self):
        return self._is_assigned
