from lxml import etree

from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.ros.robot_queries import FactoryRobotQueryElements
from himeko.transformations.ros.robot_text_generation import CreateRobotText
from himeko_lang.lang.engine.load_desc import HypergraphLoader


import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())



def main(*args):
    KINEMATIC_DESC_FOLDER = os.path.join("..", "..",  "..", "examples", "kinematics")

    PATH_META_KINEMATICS = (
        os.path.join(KINEMATIC_DESC_FOLDER, "meta_kinematics.himeko"))

    PATH_ROBOT_DESC = (
        os.path.join(KINEMATIC_DESC_FOLDER, "robotics", "anthropomorphic_arm_import.himeko")
    )
    if args is not None and len(args) > 1:
        PATH_ROBOT_DESC = args[1]
        PATH_META_KINEMATICS = args[2]
        KINEMATIC_DESC_FOLDER = args[3]
        # Logger
        logger.info("Using folder: "+KINEMATIC_DESC_FOLDER)
        logger.info("Using path: "+PATH_ROBOT_DESC)
        logger.info("Using meta path: "+PATH_META_KINEMATICS)
    #
    logger.info("Loading robot description")
    #
    paths = FactoryHypergraphElements.create_vertex_default("path_node", 0)
    paths["paths"] = [PATH_ROBOT_DESC]
    paths["meta_elements"] = [PATH_META_KINEMATICS]
    # Add hypergraph loader to the hypergraphloader
    hypergraph_loader = FactoryHypergraphElements.create_vertex_constructor_default(
        HypergraphLoader, "hypergraph_loader", 0
    )
    hypergraph_loader["path"] = paths
    res = hypergraph_loader()
    kinematics_meta, robot = res[0]
    logger.info("Robot description loaded: {}".format(robot.name))
    # Queries
    factory_query = FactoryRobotQueryElements(kinematics_meta)
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
    # Output save into URDF file in the output folder (save the output folder as the input file name)
    output_file_name_folder = os.path.basename(PATH_ROBOT_DESC).split(".")[0]
    output_folder = os.path.join("output", "urdf", output_file_name_folder)
    output_file_name = os.path.join(output_folder, output_file_name_folder + ".urdf")
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    # Save URDF
    factory_create_robot_text = CreateRobotText(kinematics_meta)
    xml_generator = factory_create_robot_text.create_robot_urdf_text()
    res_xml = xml_generator(robot)
    with open(output_file_name, "w") as f:
        f.write(etree.tostring(res_xml, pretty_print=True).decode("utf-8"))
    urdf_file = output_file_name_folder + ".urdf"
    with open(os.path.join(output_folder, "launch.sh"), "w") as f:
        f.write(CreateRobotText.create_gz_load_launch_file(urdf_file, robot))
    # Set file executable
    os.system("chmod +x "+os.path.join(output_folder, "launch.sh"))
    logger.info("URDF saved in: {}".format(output_file_name))




if __name__ == "__main__":
    main(sys.argv)