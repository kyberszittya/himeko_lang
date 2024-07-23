import unittest
from lark import Lark
import os


class BasicTestLang(unittest.TestCase):

    def setUp(self):
        self.lang_path = os.path.join("..", "..", "lang", "HimekoMetalang.lark")
        self.examples_path = os.path.join("..", "..", "examples")

    def test_ast_lark(self):
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')

    def test_ast_simple_minimal_example(self):
        p = None
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')
        p0 = os.path.join(self.examples_path, "simple", "minimal_example.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_fano_graph(self):
        p = None
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')
        p0 = os.path.join(self.examples_path, "simple", "base", "fano_graph.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_basic_hierarchy(self):
        p = None
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_basic_hierarchy.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_inheritance(self):
        p = None
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')
        p0 = os.path.join(self.examples_path, "simple", "inheritance_example.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_ast_example_fields_with_reference2(self):
        p = None
        with open(self.lang_path) as f:
            lang = f.read()
            p = Lark(lang, parser='lalr')
        p0 = os.path.join(self.examples_path, "simple", "minimal_example_fields_with_reference2.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)