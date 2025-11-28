import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetRemap


def generate_launch_description():
    """Configure ROS nodes for launch"""
    ld = LaunchDescription()
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # Start Gazebo Harmonic (empty world)
    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")),
            launch_arguments={"gz_args": "-r empty.sdf"}.items(),
        )
    )
    ld.add_action(AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(get_package_share_directory("ab2_gazebo"), "models")))

    ld.add_action(  # Spawn crazyflie in Gazebo
        include_launch_file(
            "crazyflie_description",
            "spawn_crazyflie_gz.launch.py",
            "crazyflie",
            {
                "x_pose": "0.5",
                "y_pose": "0.5",
                "z_pose": "2.0",
                "z_angle": "0.0",
            },
        )
    )
    ld.add_action(  # Spawn alphabot2 in Gazebo
        include_launch_file(
            "ab2_gazebo",
            "spawn_ab2.launch.py",
            "alphabot2",
            {
                "x_pose": "0.0",
                "y_pose": "0.0",
            },
        )
    )

    # ld.add_action(Node(
    #     package="alphabot2_position",
    #     executable="position",
    #     name="position",
    #     output="screen",
    #     parameters=[{"robot_prefix": "alphabot2"}],
    # ))

    # ld.add_action(Node(
    #     package="crazyflie_position",
    #     executable="position",
    #     name="position",
    #     output="screen",
    #     parameters=[{"robot_prefix": "crazyflie"}],
    # ))

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
                    "use_sim_time": use_sim_time,
                },
            ],
        )
    )

    # ld.add_action(
    #     Node(
    #         package="crazyflie_control",
    #         executable="control_services",
    #         output="screen",
    #         parameters=[
    #             {"hover_height": 0.5},
    #             {"robot_prefix": "/crazyflie"},
    #             {"incoming_twist_topic": "/crazyflie/input_cmd_vel"},
    #             {"max_ang_z_rate": 0.4},
    #         ],
    #     )
    # )

    ld.add_action(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory("ab2_gazebo"), "launch", "robot_state_publisher.launch.py")
            ),
            launch_arguments={"use_sim_time": use_sim_time, "frame_prefix": "alphabot2"}.items(),
        )
    )

    # ld.add_action(
    #     Node(
    #         package="rviz2",
    #         executable="rviz2",
    #         name="rviz2",
    #         output="screen",
    #         parameters=[{"use_sim_time": use_sim_time}],
    #         arguments=["-d", os.path.join(get_package_share_directory("ab2_gazebo"), "rviz", "ab2_gazebo.rviz")],
    #     )
    # )

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
