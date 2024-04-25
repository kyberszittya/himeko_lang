import unittest

from himeko.hbcm.elements.edge import HyperEdge, EnumRelationDirection
from himeko.hbcm.elements.vertex import HyperVertex
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from lang.himeko_ast.himeko_ast import transformer, create_ast
from lang.himeko_meta_parser import Lark_StandAlone


class TestBasicAstParsing(unittest.TestCase):

    def read_node(self, path):
        # Transformer
        parser = Lark_StandAlone(transformer=transformer)
        # Read file
        with open(path) as f:
            tree = parser.parse(f.read())
        self.assertIsNotNone(tree, f"Unable to read tree from path {path}")
        return tree

    def test_basic_ast_parsing(self):
        p = "../examples/simple/minimal_example_with_edges.himeko"
        root = self.read_node(p)
        self.assertIsNotNone(root, "Unable to transform tree to ast")
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
        self.assertEqual(len(n1._elements) == 0, True)
        # Get intermediate node
        n_lev_0 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_0", None))
        self.assertEqual(n_lev_0.parent.name, "context")
        self.assertEqual(len(n_lev_0._elements) == 4, True)
        # Edge creation
        hbcm_mapper.create_edges(root)
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
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
        self.assertEqual(relations[0].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[1].target.name, "node1")
        self.assertEqual(relations[1].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[2].target.name, "node2")
        self.assertEqual(relations[2].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[3].target.name, "node3")
        self.assertEqual(relations[3].direction, EnumRelationDirection.IN)

    def test_basic_ast_parsing_2(self):
        p = "../examples/simple/minimal_example_with_edges.himeko"
        root = self.read_node(p)
        self.assertIsNotNone(root, "Unable to transform tree to ast")
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
        self.assertEqual(len(n1._elements) == 0, True)
        # Get intermediate node
        n_lev_0 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_0", None))
        self.assertEqual(n_lev_0.parent.name, "context")
        self.assertEqual(len(n_lev_0._elements) == 7, True)
        # Edge creation
        edges = list(context.get_children(lambda x: isinstance(x, HyperEdge), None))
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
        self.assertEqual(relations[0].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[1].target.name, "node1")
        self.assertEqual(relations[1].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[2].target.name, "node2")
        self.assertEqual(relations[2].direction, EnumRelationDirection.OUT)
        self.assertEqual(relations[3].target.name, "node3")
        self.assertEqual(relations[3].direction, EnumRelationDirection.IN)
