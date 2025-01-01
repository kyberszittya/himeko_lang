from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.ros.urdf_queries import FactoryUrdfQueryElements
from himeko_lang.lang.engine.load_desc import HypergraphLoader


import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

KINEMATIC_DESC_FOLDER = os.path.join("..", "..",  "..", "examples", "kinematics")

TEST_CASE_META_KINEMATICS_PARSING = (
    os.path.join(KINEMATIC_DESC_FOLDER, "meta_kinematics.himeko"))

TEST_CASE_META_KINEMATICS_IMPORT_PARSING = (
    os.path.join(KINEMATIC_DESC_FOLDER, "robotics", "anthropomorphic_arm_import.himeko")
)


def main(*args):

    #
    logger.info("Loading robot description")
    #
    paths = FactoryHypergraphElements.create_vertex_default("path_node", 0)
    paths["paths"] = [TEST_CASE_META_KINEMATICS_IMPORT_PARSING]
    paths["meta_elements"] = [TEST_CASE_META_KINEMATICS_PARSING]
    # Add hypergraph loader to the hypergraphloader
    hypergraph_loader = FactoryHypergraphElements.create_vertex_constructor_default(
        HypergraphLoader, "hypergraph_loader", 0
    )
    hypergraph_loader["path"] = paths
    res = hypergraph_loader()
    kinematics_meta, robot = res[0]
    logger.info("Robot description loaded: {}".format(robot.name))
    # Queries
    factory_query = FactoryUrdfQueryElements(kinematics_meta)
    op_link = factory_query.create_query_link_stereotype()
    op_joint = factory_query.create_query_joint_stereotype()
    # Execute queries
    res_link = op_link(robot)
    res_joint = op_joint(robot)
    # Iterate over links
    logger.info("Links: ")
    for link in res_link:
        logger.info("\tLink: {}".format(link.name))
    # Iterate over joints
    logger.info("Joints: ")
    for joint in res_joint:
        logger.info("\tJoint: {}".format(joint.name))






if __name__ == "__main__":
    main(sys.argv)
