import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


def generate_launch_description():
    """Configure ROS nodes for launch"""
    ld = LaunchDescription()
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # Start Webots
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(get_package_share_directory("webots_ros2_crazyflie"), "launch", "robot_launch.py")),
        )
    )

    ld.add_action(
        Node(
            package="crazyflie_landing",
            executable="rl_model",
            name="rl_model",
            output="screen",
            parameters=[
                {
                    "onnx_path": os.path.join(
                        get_package_share_directory("crazyflie_launch"),
                        "config/crazyflie_policy.onnx",
                    ),
                    "robot_cmd_topic": "/crazyflie/input_cmd_vel",
                    "use_sim_time": use_sim_time,
                },
            ],
        )
    )

    ld.add_action(
        Node(
            package="crazyflie_control",
            executable="control_services",
            output="screen",
            parameters=[
                {"hover_height": 0.5},
                {"robot_prefix": "/crazyflie"},
                {"incoming_twist_topic": "/crazyflie/input_cmd_vel"},
                {"max_ang_z_rate": 0.4},
            ],
        )
    )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory("ab2_gazebo"), "launch", "robot_state_publisher.launch.py")
            ),
            launch_arguments={"use_sim_time": use_sim_time, "frame_prefix": "alphabot2"}.items(),
        )
    )

    ld.add_action(
        Node(
            package="crazyflie_control_manager",
            executable="crazyflie_control_manager",
            output="screen",
        )
    )

    return ld


def include_launch_file(package: str, launch_file_name: str, namespace: str, params=None) -> GroupAction:
    return GroupAction(
        actions=[
            SetRemap(src="/cmd_vel", dst=f"/{namespace}/input_cmd_vel"),
            SetRemap(src="/tf", dst=f"/{namespace}/tf"),
            SetRemap(src="/odom", dst=f"/{namespace}/odom"),
            SetRemap(src="/joint_states", dst=f"/{namespace}/joint_states"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory(package),
                        "launch",
                        launch_file_name,
                    )
                ),
                launch_arguments=params.items() if params is not None else {},
            ),
        ]
    )
