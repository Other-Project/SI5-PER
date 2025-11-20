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
    pkg_share = get_package_share_directory("crazyflie_description")
    xacro_file = os.path.join(pkg_share, "urdf", "crazyflie_body.xacro")

    # Process xacro → urdf
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Launch argument for robot name
    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value="crazyflie",
        description="Name of the robot"
    )

    # Robot State Publisher (publishes TF transforms)
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_description_config,
            "frame_prefix": "crazyflie/",
        }],
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", LaunchConfiguration("robot_name"),
            "-string", robot_description_config,
            "-x", "0.0",   # X position
            "-y", "0.0",   # Y position
            "-z", "0.5",   # Z position (height)
        ],
        output="screen",
    )

    # ROS-Gazebo bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            "config_file": os.path.join(pkg_share, "config", "ros_gz_crazyflie_bridge.yaml"),
        }],
        output="screen",
    )

    # Static transform to fix frame_id mismatch
    # Gazebo publishes as 'crazyflie/base_footprint/lidar_sensor' but actual frame is 'crazyflie/lidar_sensor'
    static_transform = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "0", "0", "0",  # x, y, z translation
            "0", "0", "0",  # roll, pitch, yaw rotation
            "crazyflie/lidar_sensor",      # parent frame
            "crazyflie/base_footprint/lidar_sensor",  # child frame (the one Gazebo publishes)
        ],
        output="screen",
    )

    return LaunchDescription([
        robot_name_arg,
        robot_state_publisher,
        spawn_robot,
        bridge,
        static_transform,
    ])
