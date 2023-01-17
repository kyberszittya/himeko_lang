import abc
from collections import deque

import numpy as np

from lang.metaelements.himekonode import HimekoNode


class HypergraphTransformer(abc.ABC):

    @abc.abstractmethod
    def encode(self, n: HimekoNode, depth: int):
        raise NotImplementedError


class HypergraphTensorTransformation(HypergraphTransformer):

    def __init__(self) -> None:
        super().__init__()
        self._node_to_index = {}
        self._index_to_node = {}
        self._edge_to_index = {}
        self._index_to_edge = {}
        self._tensor = None

    def encode(self, n: HimekoNode, depth: int):
        fringe = deque()
        fringe.appendleft((-1, n))
        cnt_nodes = 0
        cnt_edges = 0
        # Search nodes
        while len(fringe) > 0:
            d, n = fringe.popleft()
            self._node_to_index[n.uuid] = d
            self._index_to_node[d] = n
            for e1 in n.get_children_edge():
                cnt_edges += 1
                self._edge_to_index[e1.uuid] = cnt_edges
                self._index_to_edge[cnt_edges] = e1
            for n in n.get_children_node():
                cnt_nodes += 1
                fringe.appendleft((cnt_nodes, n))
        self._tensor = np.zeros((cnt_edges, cnt_nodes, cnt_nodes))
        # Search edges
        return self._tensor

