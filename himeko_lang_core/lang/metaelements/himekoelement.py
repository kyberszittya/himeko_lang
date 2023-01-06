import abc


class AbstractHimekoElement(abc.ABC):

    def __init__(self, name: str, progenitor=None):
        self._name = name
        # Progenitor (hierarchical structure)
        self._progenitor: AbstractHimekoElement = progenitor

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def progenitor(self):
        return self._progenitor


class AbstractClock(abc.ABC):
    
    @property
    def getNanoSec(self):
        return 


class HimekoElement(AbstractHimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0,
                 progenitor: AbstractHimekoElement = None):
        if not isinstance(progenitor):
            raise RuntimeError("Invalid type provided as parent")
        super(HimekoElement, self).__init__(name, progenitor)
        # Unique identifier (in certain context)
        self._uid = uid
        # Universally unique identifier
        self._uuid = uuid
        # Count
        self._cid = cid



