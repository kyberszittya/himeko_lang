from himeko.hbcm.elements.vertex import HyperVertex
from test_case_descriptions import TEST_CASE_BASIC_INHERITANCE
from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM


class TestAstParsingTemplating(TestAncestorTestCase):

    def test_basic_templating(self):
        p = TEST_CASE_BASIC_INHERITANCE
        root = self.read_node(p)
        # Ensure node is not none
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        # Get root context
        context = self.transform_to_hypergraph(root)[0]
        # Check name
        self.assertEqual(context.name, "context")
        # Get children (level 1)
        nodes = list(context.get_children(lambda x: isinstance(x, HyperVertex), 1))
        # Get node names
        node_names = set(map(lambda x: x.name, nodes))
        # Check node names
        self.assertIn("node_lev_0", node_names)
        self.assertIn("node_lev_1", node_names)
        # Get node_lev_0
        n_lev_0 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_0", None))
        # Check parent
        self.assertEqual(n_lev_0.parent.name, "context")
        # Check elements
        self.assertEqual(len(n_lev_0._elements), 4)
        # Get node_0 of node_lev_0
        n_0 = next(n_lev_0.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node0", None))
        # Check node0 has one element
        self.assertEqual(len(n_0._elements), 1)
        # Get node0 of node0
        n_0_0 = next(n_0.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node0", None))
        # Check name of node0
        self.assertEqual(n_0_0.name, "node0")
        # Check parent
        self.assertEqual(n_0_0.parent.name, "node0")
        # Check has no template
        self.assertIsNone(n_0_0.template)
        # Check node0 has no elements
        self.assertEqual(len(n_0_0._elements), 0)
        # Check parent
        self.assertEqual(n_0.parent.name, "node_lev_0")
        # Get node2 of node_lev_0
        n_2 = next(n_lev_0.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node2", None))
        # Check template
        self.assertEqual(n_2.template.name, "node0")
        # Check template parent
        self.assertEqual(n_2.template.parent.name, "node_lev_0")
        # Check node3 of node_lev_0
        n_3 = next(n_lev_0.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node3", None))
        # Check template
        self.assertEqual(n_3.template.name, "node2")
        # Check template parent
        self.assertEqual(n_3.template.parent.name, "node_lev_0")
        # Check node0 of node_lev_1
        # Get node_lev_1
        n_lev_1 = next(context.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node_lev_1", None))
        # Check parent
        self.assertEqual(n_lev_1.parent.name, "context")
        # Get node0 of node_lev_1
        n_0_1 = next(n_lev_1.get_children(lambda x: isinstance(x, HyperVertex) and x.name == "node0", None))
        # Check parent
        self.assertEqual(n_0_1.parent.name, "node_lev_1")
        # Ensure that it has no template
        self.assertIsNone(n_0_1.template)
        # Ensure it has no elements
        self.assertEqual(len(n_0_1._elements), 0)


