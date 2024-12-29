# 2023

## January

### 2023.01.04
Changing from ANTLR to LARK. LARK supposed to be faster than ANTLR, which is more suitable for the proposed embedded and robotics application area of the current project.
Furthermore, PyLARK uses the same EBNF ([ISO/IEC 14977](http://www.cl.cam.ac.uk/~mgk25/iso-14977.pdf), [RFC 5234](https://www.rfc-editor.org/rfc/rfc5234)) as ANTLR.

Tutorial used: http://blog.erezsh.com/create-a-stand-alone-lalr1-parser-in-python/

Instead of listener/visitor architecture, the PyLARK framework uses transformer paradigm, and uses a CLR parser instead of LL*.

For the meta language, a new file have been created: [HimekoMetalang.lark](himeko_lang_core/src/himeko_lang/lang/HimekoMetalang.lark)