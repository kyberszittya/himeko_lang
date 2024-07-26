import unittest
from lark import Lark
import os


class BasicTestLang(unittest.TestCase):

    def setUp(self):
        self.lang_path = os.path.join("..", "..", "lang", "HimekoMetalang.lark")
        self.examples_path = os.path.join("..", "..", "examples")

    def load_lang(self):
        with open(self.lang_path) as f:
            lang = f.read()
            return Lark(lang, parser="lalr")

    def test_ast_lark(self):
        p = self.load_lang()

    def test_ast_simple_minimal_example(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)



    def test_ast_example_basic_hierarchy(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_basic_hierarchy.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_inheritance(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "inheritance_example.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_fields_with_reference(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_fields_with_reference.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_fields_with_reference2(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_fields_with_reference2.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_fields(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_fields.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_edges(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_edges.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_hierarchy_ref_edges(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_hierarchy_ref_edges.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_hierarchy_ref_edges_evaluation(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_hierarchy_ref_edges_evaluation.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_hierarchy_ref_edges_evaluation2(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_hierarchy_ref_edges_evaluation2.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_hierarchy_ref_edges_evaluation_unknown_references(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_hierarchy_ref_edges_evaluation_unknown_references.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_hierarchy_ref_edges_with_values(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_hierarchy_ref_edges_with_values.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_minimal_example_with_multiple_edges(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_with_multiple_edges.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)