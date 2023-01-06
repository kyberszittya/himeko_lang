import abc
import hashlib

from lang.metaelements.himekoelement import AbstractHimekoElement, AbstractClock


def get_progenitor_name(el: AbstractHimekoElement, res=list()):
    res.append(el.progenitor.name)
    if el.progenitor is not None:
        return res.append(get_progenitor_name(el.progenitor))
    return res

class AbstractIdentificationStrategy(abc.ABC):

    def _generate(self, *args) -> bytes:
        m = hashlib.sha3_224()
        m.update('-'.join(map(lambda x: str(x), args)))
        return m.digest()

    @abc.abstractmethod
    def transform(self, el: AbstractHimekoElement, typedef: str, clock: AbstractClock) -> bytes:
        raise NotImplementedError


class UidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: AbstractHimekoElement, typedef: str, clock: AbstractClock) -> bytes:
        return self._generate(typedef, el.name, clock.getNanoSec())


class UuidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: AbstractHimekoElement, typedef: str, clock: AbstractClock) -> bytes:
        get_progenitor_name = lambda x: x.progenitor.name is x.progenitor is not None
        progenitor_name = ''.join(get_progenitor_name(el))
        return self._generate(typedef, progenitor_name, el.name, clock.getNanoSec())
