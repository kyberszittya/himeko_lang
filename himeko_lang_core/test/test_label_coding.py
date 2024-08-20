from collections import deque

from himeko.common.clock import NullClock
from himeko.hbcm.graph.prufer_sequence import micikievus_code, create_permutation
from himeko.hbcm.visualization.graphviz import visualize_dot_graph, create_dot_graph, create_composition_tree
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_case_descriptions import TEST_CASE_SIMPLE_FOLDER

from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM

import os


TEST_CASE_MINIMAL_DEGREE_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_structure_simple_coding.himeko")
)

TEST_CASE_MINIMAL_DEO_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_very_simple_1.himeko")
)

TEST_CASE_MINIMAL_DEO_SEQUENCE_V2 = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_very_simple_1_v2.himeko")
)

class TestBasicAstParsing(TestAncestorTestCase):

    def test_leaf_elements(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEGREE_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer()
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n0")
        leafs = set(root.get_leaf_elements())
        name_set = set([x.name for x in leafs])
        self.assertIn("n4", name_set)
        self.assertIn("n6", name_set)
        self.assertIn("n9", name_set)
        self.assertIn("n8", name_set)
        self.assertIn("n10", name_set)
        self.assertIn("n12", name_set)
        self.assertIn("n13", name_set)
        # Assert some elements not in the set
        self.assertNotIn("n0", name_set)
        self.assertNotIn("n1", name_set)
        self.assertNotIn("n2", name_set)
        self.assertNotIn("n3", name_set)
        self.assertNotIn("n5", name_set)
        self.assertNotIn("n7", name_set)
        self.assertNotIn("n11", name_set)


    def test_label_coding(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        # Generate code
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n2")
        leafs = list(root.get_leaf_elements())
        guids = set()
        # Get all nodes
        nodes = list(root.get_children(lambda x: True, depth=None))
        nodes.append(root)
        # Assert that all GUIDs are unique
        print()
        for x in nodes:
            self.assertNotIn(x.guid, guids)
            guids.add(x.guid)
            print(int.from_bytes(x.guid, "big"), x.name)
        # Generate code
        code = list(micikievus_code(root))
        print()
        print([x[0].name for x in code])
        for x in code:
            print(f"{x[0].name} -> {x[1].name}")
        code_map = dict(code)
        # Check code
        self.assertNotIn(root, code_map)
        # n1 children
        self.assertEqual(code_map[root["n1"]["n8"]], root["n1"])
        # n7 children
        self.assertEqual(code_map[root["n7"]["n9"]], root["n7"])
        self.assertEqual(code_map[root["n7"]["n10"]], root["n7"])
        self.assertEqual(code_map[root["n7"]["n6"]], root["n7"])
        # n6 children
        self.assertEqual(code_map[root["n7"]["n10"]["n4"]], root["n7"]["n10"])
        # n6 children
        self.assertEqual(code_map[root["n7"]["n6"]["n3"]], root["n7"]["n6"])
        self.assertEqual(code_map[root["n7"]["n6"]["n5"]], root["n7"]["n6"])
        # Check occurrence number
        vals = list(code_map.values())
        self.assertEqual(vals.count(root), 2)
        self.assertEqual(vals.count(root["n1"]), 1)
        self.assertEqual(vals.count(root["n7"]), 3)
        self.assertEqual(vals.count(root["n7"]["n10"]), 1)
        self.assertEqual(vals.count(root["n7"]["n6"]), 2)
        self.assertEqual(len(code), 9)
        # Create permutation
        permutation, permutation_reverse = create_permutation(code, root)
        for p in range(10):
            print(p, permutation_reverse[p].name)
            self.assertIn(p, permutation_reverse)
        # Check permutation
        self.assertEqual(permutation[root], 9)
        #self.assertEqual(permutation[root["n1"]], 4)
        #self.assertEqual(permutation[root["n7"]], 7)
        # Reconstruct tree
        import pygraphviz as pgv
        unused_numbers = set(range(10))
        used_numbers = set()
        print(unused_numbers)
        fringe = deque()
        for i in range(0, 10, -1):
            p = permutation[code[i][1]]
            if p in unused_numbers:
                unused_numbers.remove(p)
                used_numbers.add(p)
                fringe.append(i)
        G = pgv.AGraph(directed=True)
        fringe.extend(sorted(list(unused_numbers)))
        for x, y in code:
            print(x.name, y.name)
        print(unused_numbers)
        for i in range(9):
            v = fringe.pop()
            print(permutation_reverse[v].name, code[i][1].name, v)
            G.add_edge(code[i][1].name, permutation_reverse[v].name)
        G.layout(prog="dot")
        G.draw("test_reconstruction.png")
        # Visualize graph
        G = create_composition_tree(root, depth=None)
        visualize_dot_graph(G, "test_label_coding.png")


    def test_label_coding_versions(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        print()
        rootv2 = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE_V2)
        self.assertIsNotNone(rootv2, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(rootv2)
        rootv2 = hyv[0]
        print()
        self.assertEqual(root.guid, rootv2.guid)
        print("Root: ", int.from_bytes(root.guid, 'big'))
        print("Root (v2): ", int.from_bytes(rootv2.guid, 'big'))
        nodes = [
            root["n1"],
            root["n7"],
            root["n1"]["n8"],
            root["n7"]["n10"],
            root["n7"]["n10"]["n4"],
            root["n7"]["n9"],
            root["n7"]["n6"],
            root["n7"]["n6"]["n3"],
            root["n7"]["n6"]["n5"]
        ]
        self.assertEqual(root["n1"].guid, rootv2["n1"].guid)
        self.assertEqual(root["n7"].guid, rootv2["n7"].guid)
        self.assertEqual(root["n1"]["n8"].guid, rootv2["n1"]["n8"].guid)
        self.assertEqual(root["n7"]["n10"].guid, rootv2["n7"]["n10"].guid)
        self.assertEqual(root["n7"]["n10"]["n4"].guid, rootv2["n7"]["n10"]["n4"].guid)
        self.assertEqual(root["n7"]["n9"].guid, rootv2["n7"]["n9"].guid)
        self.assertEqual(root["n7"]["n6"].guid, rootv2["n7"]["n6"].guid)
        self.assertEqual(root["n7"]["n6"]["n3"].guid, rootv2["n7"]["n6"]["n3"].guid)
        self.assertEqual(root["n7"]["n6"]["n5"].guid, rootv2["n7"]["n6"]["n5"].guid)
        for e in nodes:
            print(e.name, " \t", int.from_bytes(e.guid, 'big'))


