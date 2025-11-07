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

    # Start Gazebo Harmonic (empty world)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py"
            )
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
    )
    crazyflie = include_launch_file('crazyflie_description', 'spawn_crazyflie_gz.launch.py') # Spawn crazyflie in Gazebo
    alphabot2 = include_launch_file('ab2_gazebo', 'spawn_ab2.launch.py') # Spawn alphabot2 in Gazebo


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

    joy_config = os.path.join(get_package_share_directory('teleop_twist_joy'), 'config', 'xbox.config.yaml')
    joy = Node(
        package='joy', executable='joy_node', name='joy_node',
        parameters=[{
            'device_id': 0,
            'deadzone': 0.3,
            'autorepeat_rate': 20.0,
    }, joy_config])

    return LaunchDescription([gazebo_launch, crazyflie, alphabot2, position_robot, position_drone, control_drone, joy])


def include_launch_file(package: str, launch_file_name: str) -> IncludeLaunchDescription:
    return IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory(package),
            "launch",
            launch_file_name,
        )
    ))

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
