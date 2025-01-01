from himeko_lang.lang.himeko_ast.ast_hbcm import AstHbcmTransformer
from himeko_lang.lang.himeko_meta_parser import Lark_StandAlone
from himeko_lang.lang.himeko_ast.himeko_ast import transformer

import sys




def main(*args):
    path = args[0]
    # Transformer
    parser = Lark_StandAlone(transformer=transformer)
    # Read file






if __name__ == "__main__":
    main(sys.argv)
