grammar HimekoHypergraphLang;

h_content: h_header h_context;

h_header: 'meta' h_meta ;
h_context: 'context' '{' h_node '}';
// Metadata of the hypergraph description
h_meta: desc_name=ID_NAME ('{' (h_meta_import)* '}')?;
// Import metaelement (REQ:META_01)
h_meta_import: alias=ID_NAME ':' desc_import_name=ID_NAME;
// Hypergraph description
h_node: h_element_signature '{'(h_node_element)*'}';
// Hypergraph node element
h_node_element: h_node | h_edge | h_node_field;
// Fields in node
h_node_field: name=ID_NAME h_var;
// Hyperedge definition
h_edge: h_element_signature '#' (h_edge_rel)*;
// Hypergraph relation
h_edge_rel: dir=rel_dir ref=elem_reference;
h_edge_field: space=STR h_var;
// Signature defining a hypergraph element and extension of elements (REQ:NODE_03, REQ:EDGE_05)
h_element_signature: name=ID_NAME (h_extend)?;
// Extend element
h_extend: OUT_DIR elem_reference;
// Variable definition
h_var: (h_field)*;
h_field: (value=STR | value=NUMERIC | reference=elem_reference);

rel_dir: OUT_DIR | IN_DIR | BI_DIR;

elem_reference: (value='{'ID_NAME '}' | uri=h_uri);

h_uri:  PROTOCOL_NAME '://' ID_NAME;

PROTOCOL_NAME: [a-z]+;
ID_NAME: [A-Za-z/_0-9]+;
BI_DIR: '--';
OUT_DIR: '->';
IN_DIR: '<-';
// Variable definitions
STR: '"'[A-Za-z/_0-9]*'"';
NUMERIC: [-]?[0-9]+('.'[0-9]+)?;

COMMENT : '//' .*? [\n] -> skip;
COMMENT_LONG: '/*' .*? '*/' -> skip;
// No regard of whitespace
WS      : [ \t\n\r]+ -> skip;
