import abc


class AbstractHimekoElement(abc.ABC):

    def __init__(self, name: str, progenitor=None, genichronos: int = 0):
        self._name = name
        # Progenitor (hierarchical structure)
        self._progenitor: AbstractHimekoElement = progenitor
        # Genesis time
        self._genichronos = genichronos

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def progenitor(self):
        return self._progenitor

    @property
    def genesis_time(self):
        return self._genichronos

    @property
    def genichronos(self):
        return self._genichronos


class HimekoZygote(AbstractHimekoElement):

    def __init__(self, name: str, progenitor=None):
        super(HimekoZygote, self).__init__(name, progenitor)


class AbstractClock(abc.ABC):

    def __init__(self):
        self._time_nsec = 0
        self._time_secs = 0
        # Date

    @abc.abstractmethod
    def tick(self) -> int:
        raise NotImplementedError
    
    @property
    def nano_sec(self) -> int:
        self.tick()
        return self._time_nsec

    @property
    def secs(self):
        self.tick()
        return self._time_secs

    @property
    def date(self):
        self.tick()


class HimekoElement(AbstractHimekoElement):

    def __init__(self, name: str, uuid: bytes, uid: bytes, cid: int = 0,
                 progenitor: AbstractHimekoElement = None):
        if not isinstance(progenitor, AbstractHimekoElement) and progenitor is not None:
            raise RuntimeError("Invalid type provided as parent")
        super(HimekoElement, self).__init__(name, progenitor)
        # Unique identifier (in certain context)
        self._uid = uid
        # Universally unique identifier
        self._uuid = uuid
        # Count
        self._cid = cid



