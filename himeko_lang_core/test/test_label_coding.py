
from himeko.common.clock import NullClock
from himeko.hbcm.graph.prufer_sequence import micikievus_code, create_permutation_map, create_permutation_sequence, \
    reconstruct_naive_prufer
from himeko.hbcm.visualization.graphviz import visualize_dot_graph, create_composition_tree
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
        #self.assertEqual(permutation[root["n1"]], 4)
        #self.assertEqual(permutation[root["n7"]], 7)
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
        # As in S. Caminitri et al. 2007
        degree_map = {}
        node_map = {}
        for n in root.get_all_children(lambda x: True):
            degree_map[n.guid] = n.count_composite_elements + 1
            node_map[n.guid] = n
        degree_map[root.guid] = root.count_composite_elements + 1
        node_map[root.guid] = root
        nodes = degree_map.keys()
        node_list = []
        code = []
        # Nodes
        for n in nodes:
            if degree_map[n] == 1:
                u = node_map[n].parent
                if u is None:
                    continue
                # Decrease degree of parent in the map
                degree_map[u.guid] -= 1
                # Append GUID to code
                code.append(u)
                node_list.append(node_map[n])
                while degree_map[u.guid] == 1 and u.guid < n:
                    # Add parent to fringe
                    p = u
                    u = u.parent
                    if u is None:
                        break
                    degree_map[u.guid] -= 1
                    if u.guid not in degree_map:
                        break
                    code.append(u)
                    node_list.append(node_map[p.guid])
        degree = {}
        for x in node_map:
            degree[node_map[x]] = 1
        for x in code:
            degree[x] += 1
        #
        import pygraphviz as pgv
        G = pgv.AGraph(directed=True)
        for i, c in enumerate(code):
            for j, n in enumerate(node_list):
                if degree[n] == 1:
                    degree[n] -= 1
                    degree[code[i]] -= 1
                    G.add_edge(n.name, code[i].name)
                    break
        G.layout(prog="dot")
        G.draw("test_reconstruction_naive_simple_prufer_vertex.png")



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


