from lxml import etree

from himeko.hbcm.factories.creation_elements import FactoryHypergraphElements
from himeko.transformations.ros.robot_queries import FactoryRobotQueryElements
from himeko.transformations.ros.robot_text_generation import CreateRobotText
from himeko.transformations.ros.ros_control_configuration import RosControlConfigurationClass
from himeko_lang.lang.engine.load_desc import HypergraphLoader


import sys
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def main(args):
    """
    KINEMATIC_DESC_FOLDER = os.path.join("..", "..",  "..", "examples", "kinematics")

    PATH_META_KINEMATICS = (
        os.path.join(KINEMATIC_DESC_FOLDER, "meta_kinematics.himeko"))

    PATH_ROBOT_DESC = (
        os.path.join(KINEMATIC_DESC_FOLDER, "robotics", "anthropomorphic_arm_import.himeko")
    )
    """
    if args is not None and len(args) > 1:
        PATH_ROBOT_DESC = args[0]
        PATH_META_KINEMATICS = args[1]
        KINEMATIC_DESC_FOLDER = args[2]
        # Logger
        logger.info("Using folder: "+KINEMATIC_DESC_FOLDER)
        logger.info("Using path: "+PATH_ROBOT_DESC)
        logger.info("Using meta path: "+PATH_META_KINEMATICS)
    #

if __name__ == "__main__":
    main(sys.argv[1:])