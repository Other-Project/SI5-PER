import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
import xacro


def generate_launch_description():
    """Configure ROS nodes for launch"""

    # Setup to launch a crazyflie gazebo simulation from the ros_gz_crazyflie project
    pkg_project_crazyflie_gazebo = get_package_share_directory('crazyflie_description')
    launch_file = PythonLaunchDescriptionSource(os.path.join(pkg_project_crazyflie_gazebo, 'launch', 'spawn_crazyflie_gz.launch.py'))
    crazyflie_simulation = IncludeLaunchDescription(launch_file)


    # Spawn alphabot2 in Gazebo
    pkg_project_alphabot2_gazebo = get_package_share_directory('alphabot2_description')
    launch_file = PythonLaunchDescriptionSource(os.path.join(pkg_project_alphabot2_gazebo, 'launch', 'spawn_alphabot2_gz.launch.py'))
    alphabot2 = IncludeLaunchDescription(launch_file)

    position_robot = Node(
        package="alphabot2_position",
        executable="position",
        name="position",
        output="screen",
        parameters=[{"robot_prefix": "alphabot2"}],
    )

    position_drone = Node(
        package="crazyflie_position",
        executable="position",
        name="position",
        output="screen",
        parameters=[{"robot_prefix": "crazyflie"}],
    )

    control_drone = Node(
        package="crazyflie_control",
        executable="control_services",
        output="screen",
        parameters=[
            {"hover_height": 0.5},
            {"robot_prefix": "/crazyflie"},
            {"incoming_twist_topic": "/cmd_vel"},
            {"max_ang_z_rate": 0.4},
        ],
    )

    return LaunchDescription([crazyflie_simulation, alphabot2, position_robot, position_drone, control_drone])


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
