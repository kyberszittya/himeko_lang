
from himeko.hbcm.elements.edge import HyperEdge, EnumHyperarcDirection
from himeko.hbcm.elements.element import common_ancestor
from himeko.hbcm.elements.vertex import HyperVertex
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_ast.himeko_ast import create_ast
from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM

from test_case_descriptions import TEST_CASE_BASIC_FANO, TEST_CASE_BASIC_PARSING, \
    TEST_CASE_BASIC_PARSING_2, TEST_CASE_MINIMAL_PARSING, TEST_CASE_BASIC_HIERARCHY


class TestBasicAstParsing(TestAncestorTestCase):

    def test_minimal_ast_parsing(self):
        p = TEST_CASE_MINIMAL_PARSING
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        self.assertEqual(len(hyv), 1, "Expected one root vertex")
        self.assertEqual(hyv[0].name, "context")
        self.assertEqual(len(hyv[0]._elements), 0)

    def test_basic_ast_parsing(self):
        p = TEST_CASE_BASIC_PARSING
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        create_ast(root)
        hyv = hbcm_mapper.create_root_hyper_vertices(root)
        self.assertEqual(len(hyv), 1, "Expected one root vertex")
        context = hyv[0]

        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        node_names = set(map(lambda x: x.name, nodes))

        self.assertIn("node0", node_names)
        self.assertIn("node1", node_names)
        self.assertIn("node2", node_names)
        self.assertIn("node3", node_names)
        self.assertIn("node_lev_0", node_names)
        self.assertIn("node_lev_1", node_names)
        # Get a leaf node
        n1 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node1", None))
        self.assertEqual(n1.name, "node1")
        self.assertEqual(n1.parent.name, "node_lev_0")
        self.assertEqual(len(n1._elements), 0)
        # Get intermediate node
        n_lev_0 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_0", None))
        self.assertEqual(n_lev_0.parent.name, "context")
        self.assertEqual(len(n_lev_0._elements), 4)
        # Edge creation
        hbcm_mapper.create_edges(root)
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
        for e in edges:
            e: HyperEdge
            for r in e.all_relations():
                self.assertIsNotNone(r.target)
        edge_names = set(map(lambda x: x.name, edges))
        self.assertIn("e0", edge_names)
        self.assertIn("e1", edge_names)
        self.assertIn("e2", edge_names)
        # Edge relations
        e0: HyperEdge = next(context.get_children(lambda x: isinstance(x, HyperEdge) and x.name == "e0", None))
        self.assertEqual(e0.name, "e0")
        self.assertEqual(e0.parent.name, "node_lev_0")
        hbcm_mapper.retrieve_references(hyv)
        relations = list(e0.all_relations())
        self.assertEqual(len(relations), 4)
        for rel in relations:
            self.assertEqual(rel.value, 1.0)
        self.assertEqual(relations[0].target.name, "node0")
        self.assertEqual(relations[0].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[1].target.name, "node1")
        self.assertEqual(relations[1].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[2].target.name, "node2")
        self.assertEqual(relations[2].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[3].target.name, "node3")
        self.assertEqual(relations[3].direction, EnumHyperarcDirection.IN)
        # Check if relations point to the same memory
        sel_node0 = next(context.get_children(
            lambda x: isinstance(x, HyperVertex) and x.name == "node0", None))
        self.assertIsNotNone(sel_node0)
        self.assertEqual(id(relations[0].target), id(sel_node0))
        sel_node1 = next(context.get_children(
            lambda x: isinstance(x, HyperVertex) and x.name == "node1", None))
        self.assertIsNotNone(sel_node1)
        self.assertEqual(id(relations[1].target), id(sel_node1))
        sel_node2 = next(context.get_children(
            lambda x: isinstance(x, HyperVertex) and x.name == "node2", None))
        self.assertIsNotNone(sel_node2)
        self.assertEqual(id(relations[2].target), id(sel_node2))
        sel_node3 = next(context.get_children(
            lambda x: isinstance(x, HyperVertex) and x.name == "node3", None))
        self.assertIsNotNone(sel_node3)
        self.assertEqual(id(relations[3].target), id(sel_node3))

    def test_basic_ast_parsing_2(self):
        p = TEST_CASE_BASIC_PARSING_2
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        self.assertEqual(len(hyv), 1, "Expected one root vertex")
        context = hyv[0]
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        node_names = set(map(lambda x: x.name, nodes))

        self.assertIn("node0", node_names)
        self.assertIn("node1", node_names)
        self.assertIn("node2", node_names)
        self.assertIn("node3", node_names)
        self.assertIn("node_lev_0", node_names)
        self.assertIn("node_lev_1", node_names)
        # Get a leaf node
        n1 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node1", None))
        self.assertEqual(n1.name, "node1")
        self.assertEqual(n1.parent.name, "node_lev_0")
        self.assertEqual(len(n1._elements), 0)
        # Get intermediate node
        n_lev_0 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_0", None))
        self.assertEqual(n_lev_0.parent.name, "context")
        self.assertEqual(len(n_lev_0._elements), 7)
        # Edge creation
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
        for e in edges:
            e: HyperEdge
            for r in e.all_relations():
                self.assertIsNotNone(r.target)
        edge_names = set(map(lambda x: x.name, edges))
        self.assertIn("e0", edge_names)
        self.assertIn("e1", edge_names)
        self.assertIn("e2", edge_names)
        # Edge relations
        e0: HyperEdge = next(context.get_children(lambda x: isinstance(x, HyperEdge) and x.name == "e0", None))
        self.assertEqual(e0.name, "e0")
        self.assertEqual(e0.parent.name, "node_lev_0")
        relations = list(e0.all_relations())
        self.assertEqual(len(relations), 4)
        for rel in relations:
            self.assertEqual(rel.value, 1.0)
        self.assertEqual(relations[0].target.name, "node0")
        self.assertEqual(relations[0].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[1].target.name, "node1")
        self.assertEqual(relations[1].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[2].target.name, "node2")
        self.assertEqual(relations[2].direction, EnumHyperarcDirection.OUT)
        self.assertEqual(relations[3].target.name, "node3")
        self.assertEqual(relations[3].direction, EnumHyperarcDirection.IN)

    def test_fano(self):
        p = TEST_CASE_BASIC_FANO
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        node_names = set(map(lambda x: x.name, nodes))
        self.assertEqual(len(nodes), 7)
        for i in range(0, 7):
            self.assertIn(f"n{i}", node_names)
        # Edge creation
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
        for e in edges:
            e: HyperEdge
            for r in e.all_relations():
                self.assertIsNotNone(r.target)
        edge_names = set(map(lambda x: x.name, edges))
        for i in range(0, 7):
            self.assertIn(f"e{i}", edge_names)
        # Edge relations

    def test_basic_hierarchy(self):
        p = TEST_CASE_BASIC_HIERARCHY
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        self.assertEqual(context.name, "context")
        self.assertEqual(len(context._elements), 2)
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), None))
        # Node _lev_0
        node_lev_0 = next(filter(lambda x: x.name == "node_lev_0", nodes))
        self.assertEqual(node_lev_0.name, "node_lev_0")
        self.assertEqual(node_lev_0.parent.name, "context")
        self.assertEqual(len(node_lev_0._elements), 4)
        # Children of node_lev_0
        children_node_lev_0 = list(node_lev_0.get_children(lambda x: isinstance(x, HyperVertex), None))
        # Node 0 of node_lev_0
        node0 = next(filter(lambda x: x.name == "node0", children_node_lev_0))
        self.assertEqual(node0.name, "node0")
        self.assertEqual(node0.parent.name, "node_lev_0")
        self.assertEqual(len(node0._elements), 1)
        # Node 0 children
        children_node0 = list(node0.get_children(lambda x: isinstance(x, HyperVertex), None))
        # Check node0 of node0
        node0_node0 = next(filter(lambda x: x.name == "node0", children_node0))
        self.assertEqual(node0_node0.name, "node0")
        self.assertEqual(node0_node0.parent.name, "node0")
        self.assertEqual(len(node0_node0._elements), 0)
        # Check whether other nodes have 0 children in node_leve_0
        for n in children_node_lev_0:
            if n.name != "node0":
                self.assertEqual(len(list(n.get_children(lambda x: isinstance(x, HyperVertex), None))), 0)

        # Node _lev_1
        node_lev_1 = next(filter(lambda x: x.name == "node_lev_1", nodes))
        self.assertEqual(node_lev_1.name, "node_lev_1")
        self.assertEqual(node_lev_1.parent.name, "context")
        self.assertEqual(len(node_lev_1._elements), 1)
        # Get node0 of node_lev_1
        node0 = next(filter(lambda x: x.name == "node0", list(node_lev_1.get_children(lambda x: isinstance(x, HyperVertex), None))))
        # Children of node0 in node_lev_1 is empty
        self.assertEqual(len(list(node0.get_children(lambda x: isinstance(x, HyperVertex), None))), 0)

    def test_basic_hierarchy_degrees(self):
        p = TEST_CASE_BASIC_HIERARCHY
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        self.assertEqual(context.name, "context")
        # Node _lev_0
        node_lev_0 = context["node_lev_0"]
        node_1 = context["node_lev_0"]["node1"]
        # Node_lev_1
        node_lev_1 = context["node_lev_1"]
        # Check degrees (no degrees should be present)
        self.assertEqual(node_lev_0.degree, 0)
        self.assertEqual(node_1.degree, 0)
        self.assertEqual(node_lev_1.degree, 0)

    def test_common_ancestor(self):
        p = TEST_CASE_BASIC_HIERARCHY
        root = self.read_node(p)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        context = hyv[0]
        # Nodes
        self.assertEqual(context.name, "context")
        # Node _lev_0
        node_lev_0 = context["node_lev_0"]
        node_lev_1 = context["node_lev_1"]
        node_0 = context["node_lev_0"]["node0"]["node0"]
        node_1 = context["node_lev_0"]["node1"]
        # Node_lev_1
        node_lev_1 = context["node_lev_1"]
        # Check common ancestor
        self.assertEqual(common_ancestor(node_1, node_0), node_lev_0)
        self.assertEqual(common_ancestor(node_1, node_lev_1), context)


