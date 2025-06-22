from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import HyperEdge, HyperVertex, EnumHyperarcDirection
from himeko.common.clock import SystemTimeClock
from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements

class HyMeKoVisualHypergraphFactory:
    """
    Factory class to wrap HyMeKo hypergraph creation and manipulation.
    All element creation and manipulation should go through this class.
    """

    def __init__(self):
        self.clock = SystemTimeClock()
        self.reset()

    def reset(self):
        self.nodes = []
        self.hyperedges = []
        self.connections = []
        self.attributes = []

    def create_node(self, name, x, y, radius=30, parent=None):
        from node_element import VisualNode
        timestamp = self.clock.nano_sec
        parent_hg = parent.hypergraph_element if parent is not None and hasattr(parent, "hypergraph_element") else None
        hypergraph_node = FactoryHypergraphElements.create_vertex_default(name, timestamp, parent_hg)
        visual_node = VisualNode(x, y, name, radius)
        visual_node.hypergraph_element = hypergraph_node
        self.nodes.append(visual_node)
        if parent:
            visual_node.insert_into(parent)
        return visual_node

    def create_hyperedge(self, name, x, y, width=80, height=30, parent=None):
        from edge_element import VisualHyperedge
        timestamp = self.clock.nano_sec
        parent_hg = parent.hypergraph_element if parent is not None and hasattr(parent, "hypergraph_element") else None
        hypergraph_edge = FactoryHypergraphElements.create_edge_default_attributes(name, timestamp, parent_hg)
        visual_edge = VisualHyperedge(x, y, name, width, height)
        visual_edge.hypergraph_element = hypergraph_edge
        self.hyperedges.append(visual_edge)
        if parent:
            visual_edge.insert_into(parent)
        return visual_edge

    def create_connection(self, source, target, value=None):
        from connection_element import VisualGraphConnection
        visual_conn = VisualGraphConnection(source, target, value)
        self.connections.append(visual_conn)

        # --- Associate relationship in the hypergraph model ---
        # Only add relationship if both source and target have hypergraph_element
        src_hg = getattr(source, "hypergraph_element", None)
        tgt_hg = getattr(target, "hypergraph_element", None)
        if src_hg is not None and tgt_hg is not None:
            # Convention: Node -> Hyperedge or Hyperedge -> Node
            # Add as relation to the HyperEdge's model
            if isinstance(src_hg, HyperVertex) and isinstance(tgt_hg, HyperEdge):
                # Associate node with hyperedge
                e: HyperEdge = target.hypergraph_element
                e += (src_hg, EnumHyperarcDirection.IN, 1.0)
            elif isinstance(src_hg, HyperEdge) and isinstance(tgt_hg, HyperVertex):
                # Associate node with hyperedge (reverse direction)
                e: HyperEdge = source.hypergraph_element
                e += (tgt_hg, EnumHyperarcDirection.OUT, 1.0)
        return visual_conn

    def add_attribute(self, element, attr_name):
        # Create the visual attribute
        attr = element.add_attribute(attr_name)
        # Create the hypergraph attribute and associate it
        parent_hg = getattr(element, "hypergraph_element", None)
        if parent_hg is not None:
            # Use current time as timestamp, type as "str", value as attr_name (can be customized)
            timestamp = self.clock.nano_sec
            hypergraph_attr: HypergraphAttribute = FactoryHypergraphElements.create_attribute_default(
                attr_name, None, "str", timestamp, parent_hg
            )
            # Hypergraph add unknown element
            query_value = FactoryHypergraphElements.create_query_attribute_default(
                f"{attr_name}_query", None, "str", timestamp, None)
            hypergraph_attr.value = query_value
            attr.hypergraph_element = hypergraph_attr
            # Optionally, add to parent's hypergraph attributes if such a list exists
            if hasattr(parent_hg, "attributes"):
                parent_hg.attributes.append(hypergraph_attr)
        self.attributes.append(attr)
        return attr

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def remove_hyperedge(self, edge):
        if edge in self.hyperedges:
            self.hyperedges.remove(edge)

    def remove_connection(self, conn):
        if conn in self.connections:
            self.connections.remove(conn)

    def remove_attribute(self, attr):
        if attr in self.attributes:
            self.attributes.remove(attr)

    # Additional methods for manipulation can be added here
