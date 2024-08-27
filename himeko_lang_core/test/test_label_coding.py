
from himeko.common.clock import NullClock
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.hbcm.graph.prufer_sequence import micikievus_code, create_permutation_map, create_permutation_sequence, \
    reconstruct_naive_prufer, generate_naive_prufer
from himeko.hbcm.transformations.transmission import copy_tree, transform_raw_code
from himeko.hbcm.visualization.graphviz import visualize_dot_graph, create_composition_tree, visualize_prufer_code
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from test_case_descriptions import TEST_CASE_SIMPLE_FOLDER

from test_ancestor_testcase import TestAncestorTestCase, ERROR_MSG_UNABLE_TO_TRANSFORM

import os


TEST_CASE_MINIMAL_DEGREE_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_structure_simple_coding.himeko")
)

TEST_CASE_MINIMAL_NAIVE_PRUFER_SEQUENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "coding", "composite_simple_prufer_1.himeko")
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

    def test_label_coding_numerics(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        # Generate code
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n2")
        leafs = list(root.get_leaf_elements())
        # Check leafs
        self.assertEqual(len(leafs), 5)
        self.assertIn(root["n1"]["n8"], leafs)
        self.assertIn(root["n7"]["n9"], leafs)
        self.assertIn(root["n7"]["n10"]["n4"], leafs)
        self.assertIn(root["n7"]["n6"]["n3"], leafs)
        self.assertIn(root["n7"]["n6"]["n5"], leafs)
        # Check guids
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

    def test_label_coding_guids(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        # Generate code
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n2")
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


    def test_label_coding(self):
        root = self.read_node(TEST_CASE_MINIMAL_DEO_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        # Generate code
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        self.assertEqual(root.name, "n2")
        # Get all nodes
        nodes = list(root.get_children(lambda x: True, depth=None))
        nodes.append(root)
        # Assert that all GUIDs are unique
        print()
        # Generate code
        code = list(micikievus_code(root))
        # Create permutation
        permutation, permutation_reverse = create_permutation_map(code, root)
        for p in range(10):
            print(p, permutation_reverse[p].name)
            self.assertIn(p, permutation_reverse)
        # Check permutation
        self.assertEqual(permutation[root], 9)
        perm_seq = list(create_permutation_sequence(code, permutation))
        # Reconstruct tree
        # Visualize graph
        G = create_composition_tree(root, depth=None)
        visualize_dot_graph(G, "test_label_coding.png")

    def test_reconstruct_code_prufer(self):
        # As in S. Caminitri et al. 2007
        nodes = list(range(8))
        code = [7, 3, 3, 2, 2, 2, 7]
        # Leaves
        n = len(code) + 2
        degree = {}
        for x in nodes:
            degree[x] = 1
        for x in code:
            degree[x] += 1

        #
        import pygraphviz as pgv
        G = pgv.AGraph(directed=True)
        for i in range(len(code)):
            for j in range(n):
                if degree[j] == 1:
                    degree[j] -= 1
                    degree[code[i]] -= 1
                    G.add_edge(j, code[i])
                    break
        G.layout(prog="dot")
        G.draw("test_reconstruction_naive_simple_prufer.png")

    def test_reconstruct_code_prufer_hypervertex(self):
        root = self.read_node(TEST_CASE_MINIMAL_NAIVE_PRUFER_SEQUENCE)
        self.assertIsNotNone(root, ERROR_MSG_UNABLE_TO_TRANSFORM)
        hbcm_mapper = AstHbcmTransformer(NullClock())
        hyv = hbcm_mapper.convert_tree(root)
        root = hyv[0]
        self.assertEqual(root.name, "n8")
        copy_node, list_copy_node, copy_node_map, _ = copy_tree(root)
        # Generate a code to check
        code, node_list, node_map = generate_naive_prufer(root)
        node_list.append(root)
        # Assert copied and original list of nodes are the same
        self.assertEqual(len(node_list), len(list_copy_node))
        for i in range(len(node_list)):
            self.assertEqual(node_list[i].name, list_copy_node[i].name)
            self.assertEqual(node_list[i].guid, list_copy_node[i].guid)
            self.assertEqual(node_list[i].serial, list_copy_node[i].serial)
            self.assertEqual(node_list[i].timestamp, list_copy_node[i].timestamp)
            self.assertEqual(node_list[i].label, list_copy_node[i].label)
            self.assertEqual(node_list[i].suid, list_copy_node[i].suid)

        degree = {}
        for x in node_map:
            degree[node_map[x]] = 1
        for x in code:
            degree[x] += 1
        visualize_prufer_code(code, degree, node_list, "test_reconstruction_naive_simple_prufer_vertex.png")
        # Reconstruct tree
        raw_code = [x.guid for x in code]
        node_code = [x[1] for x in copy_node]
        raw_code_, node_code_ = transform_raw_code(root)
        self.assertEqual(raw_code, raw_code_)
        self.assertEqual(node_code, node_code_)
        # Reconstruct tree
        root: HyperVertex = reconstruct_naive_prufer(raw_code, node_code, copy_node_map)
        G = create_composition_tree(root, depth=None)
        visualize_dot_graph(G, "test_label_coding_reconstructed.png")
        # Check if reiteration on new Prufer sequence is the same as previous (GUIDs)
        # Ordering is most important
        code_2, node_list_2, _ = generate_naive_prufer(root)
        node_list_2.append(root)
        for i in range(len(code)):
            self.assertEqual(code[i].guid, code_2[i].guid)
        # Permutation element
        # Check if equals with node list
        for i in range(len(node_list)):
            self.assertEqual(node_list[i].guid, root.permutation_sequence[i].guid)
            self.assertEqual(root.permutation_sequence[i].guid, node_list_2[i].guid)


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


