import os

TEST_CASE_SIMPLE_FOLDER = os.path.join("..", "examples", "simple")
TEST_CASE_BASE_FOLDER = os.path.join(TEST_CASE_SIMPLE_FOLDER, "base")

TEST_CASE_MINIMAL_PARSING = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example.himeko"))
TEST_CASE_BASIC_PARSING = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_edges.himeko"))
TEST_CASE_BASIC_PARSING_2 = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_edges.himeko"))
TEST_CASE_BASIC_FIELDS = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_fields.himeko"))
TEST_CASE_BASIC_HIERARCHY = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_basic_hierarchy.himeko"))
TEST_CASE_FIELDS_WITH_REFERENCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_fields_with_reference2.himeko"))
TEST_CASE_FIELDS_WITH_REFERENCE_2 = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_fields_with_reference.himeko"))
TEST_CASE_FIELDS_WITH_HIERARCHY_REF_EDGES = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_hierarchy_ref_edges.himeko"))
TEST_CASE_HIERARCHY_REF_EDGES = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_hierarchy_ref_edges_evaluation2.himeko"))
TEST_CASE_HIERARCHY_REF_EDGES_WITH_VALUES = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_hierarchy_ref_edges_with_values.himeko"))
TEST_CASE_MULTIPLE_EDGES = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "minimal_example_with_multiple_edges.himeko"))

TEST_CASE_BASIC_INHERITANCE = (
    os.path.join(TEST_CASE_SIMPLE_FOLDER, "inheritance_example.himeko"))

TEST_CASE_BASIC_FANO = (
    os.path.join(TEST_CASE_BASE_FOLDER, "fano_graph.himeko"))