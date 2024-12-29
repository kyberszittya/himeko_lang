from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge
from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone
from himeko_lang.lang.himeko_ast.himeko_ast import transformer


class ParserOperation(object):

    def __init__(self):
        self._parser = Lark_StandAlone(transformer=transformer)
        self._hbcm_mapper = AstHbcmTransformer()

    @property
    def parser(self):
        return self._parser

    def parse(self, text):
        return self._parser.parse(text)

    def parse_from_file(self, path):
        with open(path) as f:
            return self._parser.parse(f.read())

    def map(self, root, library_path=None):
        if library_path is not None:
            return self._hbcm_mapper.convert_tree(root, library_path)
        else:
            return self._hbcm_mapper.convert_tree(root)


class ParseDescriptionEdge(ExecutableHyperEdge, ParserOperation):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        ExecutableHyperEdge.__init__(self, name, timestamp, serial, guid, suid, label, parent)
        ParserOperation.__init__(self)

    def execute(self, *args, **kwargs):
        if self.cnt_in_relations < 1:
            text = kwargs["text"]
            # Transformer
            root = self.parser.parse(text)
            if "library_path" in kwargs:
                library_path = kwargs["library_path"]
                hyv = self.map(root, library_path)
            else:
                hyv = self.map(root)
            return hyv
        else:
            for v in self.in_relations():
                library_path = v.target["library_path"].value
                text = v.target["text"].value
                root = self.parser.parse(text)
                res = self.map(root, library_path)
                for o in self.out_relations():
                    for r in res:
                        if r.name not in o.target:
                            o.target.add_element(r)
                del res


class ParseDescriptionEdgeFromFile(ExecutableHyperEdge, ParserOperation):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        ExecutableHyperEdge.__init__(self, name, timestamp, serial, guid, suid, label, parent)
        ParserOperation.__init__(self)

    def execute(self, *args, **kwargs):
        if self.cnt_in_relations < 1:
            path = kwargs["path"]
            # Transformer
            # Read file
            root = self.parse_from_file(path)
            if "library_path" in kwargs:
                library_path = kwargs["library_path"]
                hyv = self.map(root, library_path)
            else:
                hyv = self.map(root)
            return hyv
        else:
            for v in self.in_relations():
                library_path = v.target["library_path"].value
                path = v.target["path"].value
                root = self.parse_from_file(path)
                res = self.map(root, library_path)
                for o in self.out_relations():
                    for r in res:
                        if r.name not in o.target:
                            o.target.add_element(r)
                del res
