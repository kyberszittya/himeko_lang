from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
from lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from lang.himeko_meta_parser import Lark_StandAlone
from lang.himeko_ast.himeko_ast import transformer


class ParseDescriptionEdge(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    def execute(self, *args, **kwargs):
        text = kwargs["text"]
        # Transformer
        parser = Lark_StandAlone(transformer=transformer)
        # Read file
        root = parser.parse(text)
        hbcm_mapper = AstHbcmTransformer()
        if "library_path" in kwargs:
            library_path = kwargs["library_path"]
            hyv = hbcm_mapper.convert_tree(root, library_path)
        else:
            hyv = hbcm_mapper.convert_tree(root)
        return hyv


class ParseDescriptionEdgeFromFile(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        super().__init__(name, timestamp, serial, guid, suid, label, parent)

    def execute(self, *args, **kwargs):
        path = kwargs["path"]
        # Transformer
        parser = Lark_StandAlone(transformer=transformer)
        # Read file
        with open(path) as f:
            root = parser.parse(f.read())
        hbcm_mapper = AstHbcmTransformer()
        if "library_path" in kwargs:
            library_path = kwargs["library_path"]
            hyv = hbcm_mapper.convert_tree(root, library_path)
        else:
            hyv = hbcm_mapper.convert_tree(root)
        return hyv
