
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    IfElseSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def launch_setup(context, *args, **kwargs):

    activate_diff_drive_base_controller = LaunchConfiguration("activate_diff_drive_base_controller")
    intitial_diff_drive_base_controller = "diff_drive_base_controller"

    urdf_content = open("diff_robot.urdf").read()
    robot_description = {"robot_description": urdf_content}

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{"use_sim_time": True}, robot_description],
    )
    # Start the joint state broadcaster
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )


    # There may be other controllers of the joints, but this is the initially-started one
    intitial_diff_drive_base_controller_spawner_started = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_diff_drive_base_controller, "-c", "/controller_manager"],
        condition=IfCondition(activate_diff_drive_base_controller),
    )
    intitial_diff_drive_base_controller_spawner_stopped = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[intitial_diff_drive_base_controller, "-c", "/controller_manager", "--stopped"],
        condition=UnlessCondition(activate_diff_drive_base_controller),
    )


    gz_sim_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen"
    )    
                        
    gz_sim_bridge_camera_topic = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="camera_bridge",
        parameters=[{
            'use_sim_time': True,
            'config_file': "camera_topic.yaml"
        }],
        output="screen"
    )


    nodes_to_start = [
        robot_state_publisher_node,
        joint_state_broadcaster_spawner,

        intitial_diff_drive_base_controller_spawner_started,
        intitial_diff_drive_base_controller_spawner_stopped,

        gz_sim_bridge,

        gz_sim_bridge_camera_topic,

    ]

    return nodes_to_start

def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "activate_diff_drive_base_controller",
            default_value="true",
            description="Enable headless mode for robot control (diff_drive_base_controller)",
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
