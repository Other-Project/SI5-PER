import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch configuration variables specific to simulation
    x_pose = LaunchConfiguration("x_pose", default="0.0")
    y_pose = LaunchConfiguration("y_pose", default="0.0")
    z_pose = LaunchConfiguration("z_pose", default="0.1")
    z_angle = LaunchConfiguration("z_angle", default="0.0")

    # Declare the launch arguments
    declare_x_position_cmd = DeclareLaunchArgument("x_pose", default_value="0.0", description="")
    declare_y_position_cmd = DeclareLaunchArgument("y_pose", default_value="0.0", description="")
    declare_z_position_cmd = DeclareLaunchArgument("z_pose", default_value="0.1", description="")
    declare_z_angle_cmd = DeclareLaunchArgument("z_angle", default_value="0.0", description="")

    # Package and xacro path
    pkg_share = get_package_share_directory("crazyflie_description")
    xacro_file = os.path.join(pkg_share, "urdf", "crazyflie_body.xacro")

    # Process xacro → urdf
    robot_description_config = xacro.process_file(xacro_file).toxml()

    # Launch argument for robot name
    robot_name_arg = DeclareLaunchArgument("robot_name", default_value="crazyflie", description="Name of the robot")

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            LaunchConfiguration("robot_name"),
            "-string",
            robot_description_config,
            "-x",
            x_pose,  # X position
            "-y",
            y_pose,  # Y position
            "-z",
            z_pose,  # Z position (height)
            "-Y",
            z_angle,  # Yaw rotation
        ],
        output="screen",
    )

    # ROS-Gazebo bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[
            {
                "config_file": os.path.join(pkg_share, "config", "ros_gz_crazyflie_bridge.yaml"),
            }
        ],
        output="screen",
    )

    # Laser frame fixer node
    laser_frame_fixer = Node(
        package="crazyflie_description",
        executable="laser_frame_fixer",
        name="laser_frame_fixer",
        output="screen",
    )

    return LaunchDescription(
        [
            declare_x_position_cmd,
            declare_y_position_cmd,
            declare_z_position_cmd,
            declare_z_angle_cmd,
            robot_name_arg,
            spawn_robot,
            bridge,
            # static_transform,
            laser_frame_fixer,
        ]
    )
