from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import EnumRelationDirection, HyperEdge
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko.hbcm.elements.vertex import HyperVertex
from test_case_descriptions import TEST_CASE_FIELDS_WITH_REFERENCE, TEST_CASE_HIERARCHY_REF_EDGES, \
    TEST_CASE_HIERARCHY_REF_EDGES_WITH_VALUES, TEST_CASE_BASIC_FIELDS, TEST_CASE_FIELDS_WITH_REFERENCE_2, \
    TEST_CASE_FIELDS_WITH_HIERARCHY_REF_EDGES, TEST_CASE_MULTIPLE_EDGES
from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM


class TestAstParsingWithReferences(TestAncestorTestCase):

    def test_value_fields(self):
        p = TEST_CASE_BASIC_FIELDS
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        self.assertEqual(len(nodes), 0)
        # Attributes
        attrs = list(context.get_children(lambda x: isinstance(x, HypergraphAttribute), None))
        self.assertEqual(len(attrs), 8)
        self.assertEqual(attrs[0].value, 56)
        self.assertEqual(attrs[2].value, 56.891)
        self.assertEqual(attrs[4].value, 3444.4623)
        self.assertEqual(context["pi"].value, 3.14156)
        self.assertEqual(context["vector"].value, [15.6, 17.8, 16.3, 12.3, 67.8, 45, 2])

    def test_value_hierarchy_edges(self):
        p = TEST_CASE_HIERARCHY_REF_EDGES
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        self.assertEqual(len(nodes), 11)
        # Edges
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
        # Check edges
        # Edge0
        e0 = next(filter(lambda x: x.name == 'e0', edges))
        self.assertEqual("e0", e0.name)
        rels = list(e0.all_relations())
        node0: HyperVertex = rels[0].target
        self.assertEqual("node0", node0.name)
        self.assertEqual("node0", node0.parent.name)
        node1: HyperVertex = rels[1].target
        self.assertEqual("node1", node1.name)
        self.assertEqual("node_lev_0", node1.parent.name)
        node2: HyperVertex = rels[2].target
        self.assertEqual("node2", node2.name)
        self.assertEqual("node_lev_0", node2.parent.name)
        node2: HyperVertex = rels[3].target
        self.assertEqual("node0", node2.name)
        self.assertEqual("node_lev_1", node2.parent.name)
        # Edge1
        e1 = next(filter(lambda x: x.name == 'e1', edges))
        self.assertEqual("e1", e1.name)
        rels = list(e1.all_relations())
        node0: HyperVertex = rels[1].target
        self.assertEqual("node1", node0.name)
        self.assertEqual("node0", node0.parent.name)
        self.assertEqual("node3", node0.parent.parent.name)

    def test_ref_edges_hierarchy_simple_edge(self):
        p = TEST_CASE_FIELDS_WITH_HIERARCHY_REF_EDGES
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        self.assertEqual(context.name, "context")
        # Next layer
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(nodes), 2)
        # Node names
        node_names = set(map(lambda x: x.name, nodes))
        self.assertIn("node_lev_0", node_names)
        self.assertIn("node_lev_1", node_names)
        # Get node_lev_0
        node_lev_0 = next(filter(lambda x: x.name == "node_lev_0", nodes))
        # Children of node_lev_0
        node_lev_0_children = list(node_lev_0.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(node_lev_0_children), 4)
        # Node names
        node_lev_0_children_names = set(map(lambda x: x.name, node_lev_0_children))
        self.assertIn("node0", node_lev_0_children_names)
        self.assertIn("node1", node_lev_0_children_names)
        self.assertIn("node2", node_lev_0_children_names)
        self.assertIn("node3", node_lev_0_children_names)
        # Get node0
        node0 = next(filter(lambda x: x.name == "node0", node_lev_0_children))
        # Children of node0 assert 0
        node0_children = list(node0.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(node0_children), 0)
        # Get node1
        node1 = next(filter(lambda x: x.name == "node1", node_lev_0_children))
        # Children of node1 assert 0
        node1_children = list(node1.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(node1_children), 0)
        # Get node2
        node2 = next(filter(lambda x: x.name == "node2", node_lev_0_children))
        # Children of node2 assert 0
        node2_children = list(node2.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(node2_children), 0)
        # Get node3
        node3 = next(filter(lambda x: x.name == "node3", node_lev_0_children))
        # Children of node3 assert 1
        node3_children = list(node3.get_children(lambda x: isinstance(x, HyperVertex), 1))
        self.assertEqual(len(node3_children), 1)
        # Get node 3 children node_0
        node3_children_node0 = next(filter(lambda x: x.name == "node0", node3_children))
        # Check node_0 parent
        self.assertEqual(node3_children_node0.parent.name, "node3")
        # Get node_lev_1
        node_lev_1 = next(filter(lambda x: x.name == "node_lev_1", nodes))
        # Get edge from node_lev_1
        edges = list(node_lev_1.get_children(lambda x: isinstance(x, HyperEdge), 1))
        self.assertEqual(len(edges), 1)
        # Get edge
        edge = next(filter(lambda x: x.name == "e0", edges))
        # Check edge relations
        rels = list(edge.all_relations())
        self.assertEqual(len(rels), 4)
        # Check relations
        # First relation relates to node_0 with parent node_lev_1, check parent
        self.assertEqual(rels[0].target.name, "node0")
        self.assertEqual(rels[0].target.parent.name, "node_lev_1")
        # Second relation relates to node_1 with parent node_lev_0, check parent
        self.assertEqual(rels[1].target.name, "node1")
        self.assertEqual(rels[1].target.parent.name, "node_lev_0")
        # Third relation relates to node_2 with parent node_lev_0, check parent
        self.assertEqual(rels[2].target.name, "node2")
        self.assertEqual(rels[2].target.parent.name, "node_lev_0")
        # Fourth relation relates to node_0 with parent node_lev_0, check parent
        self.assertEqual(rels[3].target.name, "node0")
        self.assertEqual(rels[3].target.parent.name, "node_lev_0")

    def test_minimal_example_multiple_edges(self):
        p = TEST_CASE_MULTIPLE_EDGES
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        # Check root context
        context = hyv[0]
        self.assertEqual(context.name, "context")
        # Get node_lev_0 of context
        node_lev_0 = next(filter(lambda x: x.name == "node_lev_0", context.get_children(lambda x: isinstance(x, HyperVertex), 1)))
        # Check node_lev_0
        self.assertEqual(node_lev_0.name, "node_lev_0")
        # Check parent
        self.assertEqual(node_lev_0.parent.name, "context")
        # Get children of node_lev_0 (nodes)
        children_node_lev_0 = list(node_lev_0.get_children(lambda x: isinstance(x, HyperVertex), 1))
        # Node count should be 6
        self.assertEqual(len(children_node_lev_0), 6)
        # Check all node names
        node_names = set(map(lambda x: x.name, children_node_lev_0))
        # Check as a cycle
        for i in range(0, 6):
            self.assertIn(f"node{i}", node_names)
        # Check edges
        edges = list(node_lev_0.get_children(lambda x: isinstance(x, HyperEdge), 1))
        # Check edge count (should be 3)
        self.assertEqual(len(edges), 3)
        # Check edge names
        edge_names = set(map(lambda x: x.name, edges))
        # Check as a cycle
        for i in range(0, 3):
            self.assertIn(f"e{i}", edge_names)
        # Check edge relations
        # Edge 0
        e0 = next(filter(lambda x: x.name == "e0", edges))
        # Check relations
        rels = list(e0.all_relations())
        # Check target names
        self.assertEqual(rels[0].target.name, "node0")
        self.assertEqual(rels[1].target.name, "node1")
        self.assertEqual(rels[2].target.name, "node2")
        self.assertEqual(rels[3].target.name, "node3")
        # Check directions
        self.assertEqual(rels[0].direction, EnumRelationDirection.OUT)
        self.assertEqual(rels[1].direction, EnumRelationDirection.OUT)
        self.assertEqual(rels[2].direction, EnumRelationDirection.OUT)
        self.assertEqual(rels[3].direction, EnumRelationDirection.IN)
        # Edge 1
        e1 = next(filter(lambda x: x.name == "e1", edges))
        # Check relations
        rels = list(e1.all_relations())
        # Check target names
        self.assertEqual(rels[0].target.name, "node3")
        self.assertEqual(rels[1].target.name, "node4")
        # Check directions
        self.assertEqual(rels[0].direction, EnumRelationDirection.OUT)
        self.assertEqual(rels[1].direction, EnumRelationDirection.IN)
        # Edge 2
        e2 = next(filter(lambda x: x.name == "e2", edges))
        # Check relations
        rels = list(e2.all_relations())
        # Check target names
        self.assertEqual(rels[0].target.name, "node5")
        self.assertEqual(rels[1].target.name, "node0")
        # Check directions
        self.assertEqual(rels[0].direction, EnumRelationDirection.IN)
        self.assertEqual(rels[1].direction, EnumRelationDirection.OUT)


    def test_value_ref_value_edges(self):
        p = TEST_CASE_HIERARCHY_REF_EDGES_WITH_VALUES
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        self.assertEqual(8, len(nodes))
        # Attributes
        edge: HyperEdge = list(context.get_children(lambda x: isinstance(x, HyperEdge) and x.name == "e0", None))[0]

        rel = list(edge.all_relations())
        # Check relations
        for r in rel:
            self.assertIsNotNone(r.target)
        # First relation
        self.assertEqual([0.85], rel[0].value)
        self.assertEqual("node0", rel[0].target.name)
        self.assertEqual("node_lev_1", rel[0].target.parent.name)
        self.assertEqual( EnumRelationDirection.OUT, rel[0].direction)
        # Next relation
        self.assertEqual([0.9], rel[1].value)
        self.assertEqual("node1", rel[1].target.name)
        self.assertEqual("node_lev_0", rel[1].target.parent.name)
        self.assertEqual(EnumRelationDirection.IN, rel[1].direction)
        # Negative relation
        self.assertEqual(rel[2].value, [-0.615])
        self.assertEqual("node2", rel[2].target.name)
        self.assertEqual("node_lev_0", rel[2].target.parent.name)
        self.assertEqual( EnumRelationDirection.OUT, rel[2].direction)
        # Vector relation
        self.assertEqual(rel[3].value, [0.5, 0.6])
        self.assertEqual("node0", rel[3].target.name)
        self.assertEqual("node_lev_0", rel[3].target.parent.name)
        self.assertEqual(EnumRelationDirection.OUT, rel[3].direction)

    def test_value_hierarchy_nodes(self):
        p = TEST_CASE_FIELDS_WITH_REFERENCE
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        self.assertEqual(len(nodes), 2)
        # Attributes
        attrs = list(context.get_children(lambda x: isinstance(x, HypergraphAttribute), None))
        # Test for value
        self.assertEqual(len(attrs), 5)
        self.assertEqual(attrs[0].value, 56)
        self.assertEqual(attrs[2].value, 56.891)
        self.assertIsInstance(attrs[4].value, HyperVertex)
        self.assertEqual(attrs[4].value.name, "node0")
        self.assertEqual(attrs[4].value.parent.name, "node")

    def test_value_hierarchy_nodes_2(self):
        p = TEST_CASE_FIELDS_WITH_REFERENCE_2
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        self.assertEqual(len(nodes), 2)
        # Attributes
        attrs = list(context.get_children(lambda x: isinstance(x, HypergraphAttribute), None))
        # Test for value
        self.assertEqual(len(attrs), 5)
        self.assertEqual(attrs[0].value, 56)
        self.assertEqual(attrs[2].value, 56.891)
        self.assertIsInstance(attrs[4].value, HyperVertex)
        self.assertEqual(attrs[4].value.name, "node0")
        self.assertEqual(attrs[4].value.parent.name, "node")

    def test_value_hierarchy_edges_degrees(self):
        p = TEST_CASE_HIERARCHY_REF_EDGES
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Check degrees
        # Nodes
        # Node 0
        node_lev_0_node1 = context["node_lev_0"]["node1"]
        self.assertEqual(1, node_lev_0_node1.degree)
        self.assertEqual(1, node_lev_0_node1.degree_in)
        self.assertEqual(0, node_lev_0_node1.degree_out)
        # Node 1
        node_lev_0_node2 = context["node_lev_0"]["node2"]
        self.assertEqual(1, node_lev_0_node2.degree)
        self.assertEqual(1, node_lev_0_node2.degree_in)
        self.assertEqual(0, node_lev_0_node2.degree_out)
