# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import wrap_to_pi

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def distance_to_platform_scalar(env: ManagerBasedRLEnv, temp: float = 0.8):
    """
    REWARD FUNCTION: Returns a SCALAR (single number).
    High reward if close to platform, low if far.
    """
    robot = env.scene["robot"]
    platform = env.scene["platform"]

    robot_pos = robot.data.root_pos_w
    platform_pos = platform.data.root_pos_w

    target_pos = platform_pos.clone()
    target_pos[:, 2] += 0.1

    distance = torch.linalg.norm(robot_pos - target_pos, dim=1)

    return 1 - torch.tanh(distance / temp)


def relative_pos_to_platform_vector(env: ManagerBasedRLEnv):
    """
    OBSERVATION FUNCTION: Returns a VECTOR (x, y, z).
    Tells the robot the direction to the platform.
    """
    robot = env.scene["robot"]
    platform = env.scene["platform"]

    robot_pos = robot.data.root_pos_w
    platform_pos = platform.data.root_pos_w

    target_pos = platform_pos.clone()
    target_pos[:, 2] += 0.1

    return target_pos - robot_pos


def root_height_below(env: ManagerBasedRLEnv, minimum_height: float,
                      asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    """Terminate if the asset's root height is below the minimum height."""
    asset = env.scene[asset_cfg.name]
    return asset.data.root_pos_w[:, 2] < minimum_height


def root_height_above(env: ManagerBasedRLEnv, maximum_height: float,
                      asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    """Terminate if the asset's root height is above the maximum height."""
    asset = env.scene[asset_cfg.name]
    return asset.data.root_pos_w[:, 2] > maximum_height
