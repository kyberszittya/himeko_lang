 import os
from lark import Lark
import unittest


class BasicTestLang(unittest.TestCase):

    def setUp(self):
        self.lang_path = os.path.join("..",  "src", "lang", "HimekoMetalang.lark")
        self.examples_path = os.path.join("..", "examples")

    def load_lang(self):
        with open(self.lang_path) as f:
            lang = f.read()
            return Lark(lang, parser="lalr")

    def test_ast_example_fano_graph(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "simple", "base", "fano_graph.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_simple_kinematics(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "kinematics", "simple_kinematics.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_simple_fanuc_arm_test(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "kinematics", "kamu_fanuc.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_simple_very_simple_kinematics(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "kinematics", "very_simple_kinematics.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)

    def test_simple_very_simple_kinematics_with_primitives(self):
        p = self.load_lang()
        p0 = os.path.join(self.examples_path, "kinematics", "very_simple_kinematics_with_primitives.himeko")
        with open(p0) as f:
            text = p.parse(f.read())
            print(text)
