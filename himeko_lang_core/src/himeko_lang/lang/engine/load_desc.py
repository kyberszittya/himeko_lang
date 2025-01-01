from himeko.hbcm.elements.executable.edge import ExecutableHyperEdge

import logging
import os

from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone
from himeko_lang.lang.himeko_ast.himeko_ast import transformer


class HypergraphLoader(ExecutableHyperEdge):

    def __init__(self, name: str, timestamp: int, serial: int, guid: bytes, suid: bytes, label: str, parent):
        ExecutableHyperEdge.__init__(self, name, timestamp, serial, guid, suid, label, parent)
        # Transformation
        self.parser = Lark_StandAlone(transformer=transformer)
        self.hbcm_mapper = AstHbcmTransformer()
        # Logging
        self.logger = logging.getLogger(__name__)

    def read_node(self, path):
        # Read file
        with open(path) as f:
            tree = self.parser.parse(f.read())
        # If tree is None, raise an error
        if tree is None:
            raise ValueError(f"Unable to read tree from path {path}")
        return tree

    def operate(self, *args, **kwargs):
        # Assert there is a hypergraph containing the path to the meta elements and the files to load
        if self['path'] is None:
            raise ValueError("Hypergraph containing the file path is not provided")
        # Extract values from the path hypergraph
        hy_path = self['path']
        # Assert the node has a field for paths
        if 'paths' not in hy_path:
            raise ValueError("Hypergraph does not contain paths")
        # Extract meta elements path
        meta_elements_path = hy_path['meta_elements']
        # Assert the meta elements path is not empty
        if not meta_elements_path:
            raise ValueError("No meta elements path provided")
        # Extract the paths
        paths = hy_path['paths']
        # Assert the paths are not empty
        if not paths:
            raise ValueError("No paths provided")

        meta_folders = []
        # Load the meta elements
        for meta_path in meta_elements_path:
            meta_tree = self.read_node(meta_path)
            meta = self.hbcm_mapper.convert_tree(meta_tree, )
            # Get meta folder
            meta_folder = os.path.dirname(meta_path)
            # Append the meta folder
            meta_folders.append(meta_folder)
        # Collect results
        results = []
        # Iterate over the paths
        for path in paths:
            # Read file
            tree = self.read_node(path)
            # Get parent folder
            parent_folder = os.path.dirname(path)
            # Convert the tree
            hyv = self.hbcm_mapper.convert_tree(tree, meta_folders + [parent_folder])
            # Append the results
            results.append(hyv)
        return results

