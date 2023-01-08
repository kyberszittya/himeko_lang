import abc
import hashlib

from lang.metaelements.himekoelement import AbstractHimekoElement, HimekoZygote


def get_progenitor_name(el: AbstractHimekoElement, res=list()):

    if el.progenitor is not None:
        res.append(el.progenitor.name)
        return res.append(get_progenitor_name(el.progenitor))

    return res


class AbstractIdentificationStrategy(abc.ABC):

    def _generate(self, *args) -> bytes:
        m = hashlib.sha3_224()
        m.update('-'.join(map(lambda x: str(x), args)).encode("utf-8"))
        return m.digest()

    @abc.abstractmethod
    def transform(self, el: HimekoZygote, typedef: str, time: int) -> bytes:
        raise NotImplementedError


class UidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: HimekoZygote, typedef: str, time: int) -> bytes:
        return self._generate(typedef, el.name, time)


class UuidIdentificationStrategy(AbstractIdentificationStrategy):

    def transform(self, el: HimekoZygote, typedef: str, time: int) -> bytes:
        progenitor_name = ''.join(get_progenitor_name(el))
        return self._generate(typedef, progenitor_name, el.name, time)
