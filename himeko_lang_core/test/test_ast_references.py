from himeko.hbcm.elements.attribute import HypergraphAttribute
from himeko.hbcm.elements.edge import EnumRelationDirection, HyperEdge
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko.hbcm.elements.vertex import HyperVertex
from test_case_descriptions import TEST_CASE_FIELDS_WITH_REFERENCE, TEST_CASE_HIERARCHY_REF_EDGES, \
    TEST_CASE_HIERARCHY_REF_EDGES_WITH_VALUES, TEST_CASE_BASIC_FIELDS, TEST_CASE_FIELDS_WITH_REFERENCE_2
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