import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    frame_prefix = LaunchConfiguration("frame_prefix", default="")

    urdf_path = os.path.join(get_package_share_directory("crazyflie_description"), "urdf", "crazyflie_body.xacro")
    robot_desc = xacro.process_file(urdf_path).toxml()

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="false", description="Use simulation (Gazebo) clock if true"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "robot_description": robot_desc,
                        "frame_prefix": PythonExpression(["'", frame_prefix, "/'"]),
                    }
                ],
            ),
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name="static_tf_pub",
                arguments=["0", "0", "0", "0", "0", "0", "world", PythonExpression(["'", frame_prefix, "/base_footprint'"])],
            ),
        ]
    )
