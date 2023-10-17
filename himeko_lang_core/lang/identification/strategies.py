import abc
import hashlib

from lang.graph.search_strategies import get_progenitor_chain
from lang.metaelements.himekoelement import HimekoConcept


class AbstractIdentificationStrategy(abc.ABC):

    def _generate(self, *args) -> bytes:
        m = hashlib.sha3_224()
        m.update('-'.join(map(lambda x: str(x), args)).encode("utf-8"))
        return m.digest()

    @abc.abstractmethod
    def transform(self, el: HimekoConcept, typedef: str, time: int) -> bytes:
        raise NotImplementedError


class UidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: HimekoConcept, typedef: str, time: int) -> bytes:
        return self._generate(typedef, el.name, time)


class UuidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: HimekoConcept, typedef: str, time: int) -> bytes:
        progenitor_name = '/'.join(get_progenitor_chain(el)[1:])
        return self._generate(typedef, progenitor_name, el.name, time)
