from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

from himeko_parser.gen.hypergraphlang import HimekoHypergraphLangParser
from himeko_parser.gen.hypergraphlang.HimekoHypergraphLangLexer import HimekoHypergraphLangLexer
from himeko_parser.gen.hypergraphlang.HimekoHypergraphLangParser import HimekoHypergraphLangParser
from himeko_parser.gen.hypergraphlang.HimekoHypergraphLangVisitor import HimekoHypergraphLangVisitor


class HypergraphVisitor(HimekoHypergraphLangVisitor):



    def visitH_meta(self, ctx: HimekoHypergraphLangParser.H_metaContext):
        print(ctx.desc_name.text)
        return self.visitChildren(ctx)

    def visitH_edge(self, ctx: HimekoHypergraphLangParser.H_edgeContext):
        print(ctx.h_element_signature().name.text)
        return self.visitChildren(ctx)

    def visitH_node(self, ctx:HimekoHypergraphLangParser.H_nodeContext):
        print(ctx.h_element_signature().name.text)
        return self.visitChildren(ctx)


def main():
    fname = "minimal_example.himeko"
    input_stream = FileStream(fname)
    lexer = HimekoHypergraphLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = HimekoHypergraphLangParser(stream)
    tree = parser.h_content()
    visitor = HypergraphVisitor()
    visitor.visit(tree)



if __name__ == "__main__":
    main()