# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs import mdp as std_mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass
from isaaclab_assets import CRAZYFLIE_CFG  # isort: skip

from . import mdp
from ....assets import ALPHABOT_CFG


##
# Pre-defined configs
##


##
# Scene definition
##


@configclass
class CrazyflieSceneCfg(InteractiveSceneCfg):
    """Configuration for a quadcopter scene."""

    # ground plane
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(size=(100.0, 100.0)),
    )

    # robot
    robot: ArticulationCfg = CRAZYFLIE_CFG.replace(prim_path="/World/envs/env_.*/Robot")

    # lights
    dome_light = AssetBaseCfg(
        prim_path="/World/DomeLight",
        spawn=sim_utils.DomeLightCfg(color=(0.9, 0.9, 0.9), intensity=500.0),
    )

    # platform
    platform: ArticulationCfg = ALPHABOT_CFG.replace(
        prim_path="/World/envs/env_.*/Platform"
    )


##
# MDP settings
##


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""
    body_joint_vel = mdp.JointVelocityActionCfg(
        asset_name="robot",
        joint_names=[".*"],
        scale=100,
        offset=2000,
    )


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        # observation terms (order preserved)
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel)
        distance_to_platform = ObsTerm(func=mdp.relative_pos_to_platform_vector)

        def __post_init__(self) -> None:
            self.enable_corruption = False
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""

    # reset
    reset_root = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-1.0, 1.0), "y": (-1.0, 1.0), "z": (1.5, 1.5)},
            "velocity_range": {"x": (0, 0), "y": (0, 0), "z": (0, 0)},
            "asset_cfg": SceneEntityCfg("robot"),
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""

    # (1) Constant running reward
    alive = RewTerm(func=mdp.is_alive, weight=5.0)

    # (2) Target reward
    landing_reward = RewTerm(
        func=mdp.distance_to_platform_scalar,
        weight=2.0,
    )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    # (1) Time out
    time_out = DoneTerm(func=mdp.time_out, time_out=True)

    print(f'Time out term: {time_out}')

    # (2) Crash: Reset if robot hits the ground
    crash = DoneTerm(
        func=mdp.root_height_below,
        params={"minimum_height": 0.1},
    )

    print(f'Crash term: {crash}')

    # (3) Fly Away: Reset if robot flies too high
    fly_away = DoneTerm(
        func=mdp.root_height_above,
        params={"maximum_height": 2.0},
    )

    print(f'Fly away term: {fly_away}')


##
# Environment configuration
##


@configclass
class CrazyflieEnvCfg(ManagerBasedRLEnvCfg):
    # Scene settings
    scene: CrazyflieSceneCfg = CrazyflieSceneCfg(num_envs=4096, env_spacing=4.0)
    # Basic settings
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()
    # MDP settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()

    # Post initialization
    def __post_init__(self) -> None:
        """Post initialization."""
        # general settings
        self.decimation = 2
        self.episode_length_s = 5
        # viewer settings
        self.viewer.eye = (3.0, 3.0, 3.0)
        # simulation settings
        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation
