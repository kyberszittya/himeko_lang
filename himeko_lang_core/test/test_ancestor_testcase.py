import unittest
from lang.himeko_meta_parser import Lark_StandAlone
from lang.himeko_ast.himeko_ast import transformer


ERROR_MSG_UNABLE_TO_TRANSFORM: str = "Unable to transform tree to ast"

class TestAncestorTestCase(unittest.TestCase):

    def read_node(self, path):
        # Transformer
        parser = Lark_StandAlone(transformer=transformer)
        # Read file
        with open(path) as f:
            tree = parser.parse(f.read())
        self.assertIsNotNone(tree, f"Unable to read tree from path {path}")
        return tree