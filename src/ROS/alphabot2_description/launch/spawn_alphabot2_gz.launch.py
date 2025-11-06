from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os
import xacro


def generate_launch_description():
    # Package and xacro path
    pkg_share = get_package_share_directory("alphabot2_description")
    xacro_file = os.path.join(pkg_share, "urdf", "alphabot2.urdf")

    # Process xacro → urdf
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Launch argument for robot name
    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="alphabot2",
        description="Name of the robot"
    )

    # Spawn robot in Gazebo
    spawn_robot = spawn_in_gazebo(
        "alphabot2", robot_description_config, (0.0, 2.0, 0.0)
    )

    # ROS-Gazebo bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            "config_file": os.path.join(pkg_share, "config", "ros_gz_alphabot2_bridge.yaml"),
        }],
        output="screen",
    )

    return LaunchDescription([
        robot_name_arg,
        spawn_robot,
        bridge,
    ])

def spawn_in_gazebo(
    name: str, robot_description_config: str, pos: tuple[float, float, float]
) -> Node:
    return Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            name,
            "-string",
            robot_description_config,
            "-x",
            str(pos[0]),  # X position
            "-y",
            str(pos[1]),  # Y position
            "-z",
            str(pos[2]),  # Z position (height)
        ],
        output="screen",
    )
