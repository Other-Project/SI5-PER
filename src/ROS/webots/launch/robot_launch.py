#
#  ...........       ____  _ __
#  |  ,-^-,  |      / __ )(_) /_______________ _____  ___
#  | (  O  ) |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  | / ,..´  |    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#     +.......   /_____/_/\__/\___/_/   \__,_/ /___/\___/

# MIT License

# Copyright (c) 2023 Bitcraze


"""
file: robot_launch.py

Launch Webots Crazyflie ROS2 driver.

Author:   Kimberly McGuire (Bitcraze AB)
"""

import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.substitutions.path_join_substitution import PathJoinSubstitution
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher


def generate_launch_description():
    package_dir = get_package_share_directory("webots")
    world = LaunchConfiguration("world")

    webots = WebotsLauncher(world=PathJoinSubstitution([package_dir, "worlds", world]), ros2_supervisor=True)

    crazyflie_description_path = os.path.join(package_dir, "resource", "crazyflie_webots.urdf")
    crazyflie_driver = WebotsController(
        robot_name="Crazyflie",
        parameters=[
            {"robot_description": crazyflie_description_path},
        ],
        remappings=[("/crazyflie/cmd_vel", "/cmd_vel"), ("/crazyflie/odom", "/odom")],
        respawn=True,
    )

    platform_description_path = os.path.join(get_package_share_directory("ab2_description"), "urdf", "ab2.urdf")
    platform_driver = WebotsController(
        robot_name="Alphabot2",
        parameters=[{"robot_description": platform_description_path}],
        remappings=[("/alphabot2/cmd_vel", "/cmd_vel"), ("/alphabot2/odom", "/odom")],
        respawn=True,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value="crazyflie_apartment.wbt",
                description="Choose one of the world files from `/webots/worlds` directory",
            ),
            webots,
            webots._supervisor,
            crazyflie_driver,
            platform_driver,
            # This action will kill all nodes once the Webots simulation has exited
            launch.actions.RegisterEventHandler(
                event_handler=launch.event_handlers.OnProcessExit(
                    target_action=webots,
                    on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
                )
            ),
        ]
    )
