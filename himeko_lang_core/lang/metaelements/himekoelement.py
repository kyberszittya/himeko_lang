import abc
import typing
from collections import deque


class AbstractHimekoInfoChondrium(abc.ABC):

    def __init__(self, name: str, genichronos: int = 0):
        self._name = name
        self._genichronos = genichronos

    @property
    def name(self) -> str:
        return self._name

    @property
    def genichronos(self):
        return self._genichronos


class AbstractHimekoRoot(AbstractHimekoInfoChondrium):

    def __init__(self, name: str, target: AbstractHimekoInfoChondrium, genichronos: int = 0):
        super(AbstractHimekoRoot, self).__init__(name, genichronos)
        self._target = target

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, val):
        self._source = val

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, val):
        self._target = val


class AbstractHimekoElement(AbstractHimekoInfoChondrium):

    def __init__(self, name: str, progenitor=None, genichronos: int = 0):
        super(AbstractHimekoElement, self).__init__(name, genichronos)
        # Progenitor (hierarchical structure)
        self._progenitor: AbstractHimekoElement = progenitor

    @property
    def progenitor(self):
        return self._progenitor

    @property
    def genesis_time(self):
        return self._genichronos


class HimekoConcept(AbstractHimekoElement):

    def __init__(self, name: str, progenitor=None):
        super(HimekoConcept, self).__init__(name, progenitor)


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
        # TODO: finish date handling
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
        # Elements
        self._elements_by_cid = {}
        self._elements_by_uid = {}
        # Storing unknown elements
        self._unknown_elements = set()

    @property
    def uid(self):
        return self._uid

    @property
    def uuid(self):
        return self._uuid

    def get_element_by_name(self, name: str):
        return filter(lambda x: x.name == name, self._elements_by_uid.values())

    def search_for_index_elementtree(self, query: typing.Iterable[str]):
        q = list(query)
        ref_name = '/'.join(query)
        # Count
        cnt_match = 0
        start = self
        # Set
        while start is not None:
            visited_set = set()
            # Search for first element
            fringe = deque()
            fringe.appendleft((start, 0))
            while len(fringe) != 0:
                current, cursor_query_element = fringe.pop()
                visited_set.add(current.uuid)
                if current.name == q[cursor_query_element]:
                    cursor_query_element += 1
                    if cursor_query_element == len(q):
                        cnt_match += 1
                        if ref_name in self._unknown_elements:
                            self._unknown_elements.remove(ref_name)
                        yield current
                for p in current._elements_by_uid.values():
                    if p.uuid not in visited_set and cursor_query_element < len(q):
                        fringe.append((p, cursor_query_element))
            start = start.progenitor
        # If no match
        if cnt_match == 0:
            self._unknown_elements.add(ref_name)

    def search_reference_in_context(self, query: list[str], parent) -> typing.Optional[AbstractHimekoElement]:
        if len(query) == 1:
            if parent is not None:
                try:
                    referenced_el = next(parent.get_element_by_name(query[0]))
                except StopIteration:
                    referenced_el = None
            else:
                raise RuntimeError("Invalid graph definition")
        else:
            try:
                referenced_el = next(self.search_for_index_elementtree(query))
            except StopIteration:
                referenced_el = None
        return referenced_el

