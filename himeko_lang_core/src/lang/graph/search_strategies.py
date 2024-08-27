import typing

from lang.metaelements.himekoelement import AbstractHimekoElement, HimekoElement


def get_progenitor_chain(el: AbstractHimekoElement, res=None):
    if res is None:
        res = []
    res.append(el.name)
    if el.progenitor is not None:
        return get_progenitor_chain(el.progenitor, res)
    return res




