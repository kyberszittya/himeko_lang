import abc
from collections import deque

import numpy as np

from lang.metaelements.himekonode import HimekoNode
from lang.metaelements.himekoedge import HimekoEdge, RelationDirection


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
        # Edge fringe
        fringe_edge = deque()
        # Search nodes
        while len(fringe) > 0:
            d, n = fringe.popleft()
            self._node_to_index[n.uuid] = d
            self._index_to_node[d] = n
            for e_out in n.get_children_edge():

                self._edge_to_index[e_out.uuid] = cnt_edges
                self._index_to_edge[cnt_edges] = e_out
                # Add edge to fringe
                fringe_edge.appendleft(e_out)
                cnt_edges += 1
            for n in n.get_children_node():
                fringe.appendleft((cnt_nodes, n))
                cnt_nodes += 1
        self._tensor = np.zeros((cnt_edges, cnt_nodes + 1, cnt_nodes + 1))
        while len(fringe_edge) > 0:
            e: HimekoEdge = fringe_edge.popleft()
            i_e = self._edge_to_index[e.uuid]
            _out = e.outgoing_targets()
            _in = e.incoming_targets()
            # Outgoing edges
            for e_in in _in:
                for e_out in _out:
                    if self._node_to_index[e_in[0]] != self._node_to_index[e_out[0]]:
                        self._tensor[i_e, self._node_to_index[e_in[0]], self._node_to_index[e_out[0]]] = 1.0
                        # Set incidence sub-tensor
                        self._tensor[i_e, cnt_nodes, self._node_to_index[e_out[0]]] = 1.0
                        self._tensor[i_e, self._node_to_index[e_out[0]], cnt_nodes] = 1.0
                # Incoming edges
                if e_in[2] == RelationDirection.INCOMING:
                    self._tensor[i_e, cnt_nodes, self._node_to_index[e_in[0]]] = -1.0
                    self._tensor[i_e, self._node_to_index[e_in[0]], cnt_nodes] = -1.0
                # Homogeneous coordinate
                self._tensor[i_e, cnt_nodes, cnt_nodes] = 1.0
        return self._tensor, cnt_nodes, cnt_edges

