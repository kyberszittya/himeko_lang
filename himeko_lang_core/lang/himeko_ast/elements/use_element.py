from dataclasses import dataclass

from lang.himeko_ast.elements.meta_elements import _Ast
from lang.himeko_ast.elements.reference import ElementReference


@dataclass
class HiUse(_Ast):
    reference: ElementReference

    def __init__(self, reference: ElementReference):
        self.reference = reference
