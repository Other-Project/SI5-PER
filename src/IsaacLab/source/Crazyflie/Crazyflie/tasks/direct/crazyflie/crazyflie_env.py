# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import gymnasium as gym
import isaaclab.sim as sim_utils
import torch
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.envs.ui import BaseEnvWindow
from isaaclab.markers import CUBOID_MARKER_CFG  # isort: skip
from isaaclab.markers import VisualizationMarkers
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
from isaaclab.utils.math import subtract_frame_transforms, quat_apply
from isaaclab_assets import ANYDRIVE_3_SIMPLE_ACTUATOR_CFG  # isort: skip
##
# Pre-defined configs
##
from isaaclab_assets import CRAZYFLIE_CFG  # isort: skip

from ....assets import ALPHABOT_CFG, ALPHABOT_JOINTS_NAMES, ACTUATORS_LEFT_WHEEL, ACTUATORS_RIGHT_WHEEL


class CrazyflieEnvWindow(BaseEnvWindow):
    """Window manager for the Quadcopter environment."""

    def __init__(self, env: CrazyflieEnv, window_name: str = "IsaacLab"):
        """Initialize the window.

        Args:
            env: The environment object.
            window_name: The name of the window. Defaults to "IsaacLab".
        """
        # initialize base window
        super().__init__(env, window_name)
        # add custom UI elements
        with self.ui_window_elements["main_vstack"]:
            with self.ui_window_elements["debug_frame"]:
                with self.ui_window_elements["debug_vstack"]:
                    # add command manager visualization
                    self._create_debug_vis_ui_element("targets", self.env)


@configclass
class CrazyflieEnvCfg(DirectRLEnvCfg):
    # env
    episode_length_s = 15.0
    decimation = 2
    action_space = 4
    observation_space = 10
    state_space = 0
    debug_vis = True

    ui_window_class_type = CrazyflieEnvWindow

    # simulation
    sim: SimulationCfg = SimulationCfg(
        dt=1 / 100,
        render_interval=decimation,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    # scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096, env_spacing=2.5, replicate_physics=True, clone_in_fabric=True
    )

    # drone
    robot: ArticulationCfg = CRAZYFLIE_CFG.replace(prim_path="/World/envs/env_.*/Robot")

    # Velocity command limits
    max_linear_velocity = 0.5  # m/s
    max_angular_velocity_z = 0.4  # rad/s

    # tilt constraint
    tilt_limit_deg = 30.0

    # alpha bot
    platform: ArticulationCfg = ALPHABOT_CFG.replace(
        prim_path="/World/envs/env_.*/Platform"
    )

    # reward scales
    lin_vel_reward_scale = -0.05
    ang_vel_reward_scale = -0.01
    distance_to_goal_reward_scale = 15.0
    tilt_constraint_reward_scale = -5.0
    unsafe_velocity_reward_scale = -1.0

    # random pose range
    platform_spawn_range_xy = 3.0
    platform_spawn_z = 0.0
    drone_min_height = 0.4
    drone_max_height = 0.6

    # Alpha bot movement parameters
    platform_max_linear_velocity = 0.5  # m/s
    platform_max_angular_velocity = 1.0  # rad/s


class CrazyflieEnv(DirectRLEnv):
    cfg: CrazyflieEnvCfg

    def __init__(self, cfg: CrazyflieEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Velocity commands
        self._actions = torch.zeros(self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device)
        self._drone_target_lin_vel_b = torch.zeros(self.num_envs, 3, device=self.device)
        self._drone_target_ang_vel_b = torch.zeros(self.num_envs, 3, device=self.device)

        # Platform wheel velocities for differential drive
        self._platform_wheel_vel = None
        self._platform_joint_indices = None

        # Platform target velocities (linear and angular)
        self._platform_target_lin_vel = torch.rand(self.num_envs, 3, device=self.device) / 2.0

        # Goal position (platform center)
        self._desired_pos_w = torch.zeros(self.num_envs, 3, device=self.device)

        # Logging
        self._episode_sums = {
            key: torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            for key in [
                "lin_vel",
                "ang_vel",
                "distance_to_goal",
                "tilt_constraint",
                "unsafe_velocity",
            ]
        }
        # Get specific body indices
        self._body_id = self._robot.find_bodies("body")[0]
        self._robot_mass = self._robot.root_physx_view.get_masses()[0].sum()
        self._gravity_magnitude = torch.tensor(self.sim.cfg.gravity, device=self.device).norm()
        self._robot_weight = (self._robot_mass * self._gravity_magnitude).item()

        # Initialize platform joint indices and velocities
        wheel_joint_names = [
            ALPHABOT_JOINTS_NAMES[ACTUATORS_LEFT_WHEEL],
            ALPHABOT_JOINTS_NAMES[ACTUATORS_RIGHT_WHEEL]
        ]
        self._platform_joint_indices = self._platform.find_joints(wheel_joint_names)[0]
        self._platform_wheel_vel = torch.zeros(
            self.num_envs,
            len(self._platform_joint_indices),
            device=self.device
        )

        # add handle for debug visualization (this is set to a valid handle inside set_debug_vis)
        self.set_debug_vis(self.cfg.debug_vis)

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self._platform = Articulation(self.cfg.platform)
        self.scene.articulations["robot"] = self._robot
        self.scene.articulations["platform"] = self._platform

        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        # clone and replicate
        self.scene.clone_environments(copy_from_source=False)
        # we need to explicitly filter collisions for CPU simulation
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        # add lights
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor):
        self._actions = actions.clone().clamp(-1.0, 1.0)

        self._drone_target_lin_vel_b[:, :3] = self._actions[:, :3] * self.cfg.max_linear_velocity

        self._drone_target_ang_vel_b[:, 0] = 0.0
        self._drone_target_ang_vel_b[:, 1] = 0.0
        self._drone_target_ang_vel_b[:, 2] = self._actions[:, 3] * self.cfg.max_angular_velocity_z

    def _apply_action(self):
        dt = self.sim.cfg.dt * self.cfg.decimation

        drone_target_lin_vel_w = quat_apply(
            self._robot.data.root_quat_w,
            self._drone_target_lin_vel_b
        )

        drone_target_ang_vel_w = quat_apply(
            self._robot.data.root_quat_w,
            self._drone_target_ang_vel_b
        )

        self._robot.write_root_velocity_to_sim(
            torch.cat([drone_target_lin_vel_w, drone_target_ang_vel_w], dim=-1)
        )

        # Apply platform control
        self._platform.set_joint_velocity_target(
            self._platform_wheel_vel,
            joint_ids=self._platform_joint_indices
        )
        # Change the platform position based on its velocity
        new_platform_pos = self._platform.data.root_pos_w + self._platform_target_lin_vel * dt
        new_platform_quat = self._platform.data.root_quat_w
        self._platform.write_root_pose_to_sim(torch.cat([new_platform_pos, new_platform_quat], dim=-1))

    def _get_observations(self) -> dict:
        self._desired_pos_w = self._platform.data.root_pos_w.clone()
        self._desired_pos_w[:, 2] += 0.1
        desired_pos_b, _ = subtract_frame_transforms(
            self._robot.data.root_pos_w, self._robot.data.root_quat_w, self._desired_pos_w
        )
        obs = torch.cat(
            [
                self._robot.data.root_lin_vel_b,
                self._robot.data.root_quat_w,
                desired_pos_b,
            ],
            dim=-1,
        )
        observations = {"policy": obs}
        return observations

    def _get_rewards(self) -> torch.Tensor:
        lin_vel = torch.sum(torch.square(self._robot.data.root_lin_vel_b), dim=1)
        ang_vel = torch.sum(torch.square(self._robot.data.root_ang_vel_b), dim=1)
        distance_to_goal = torch.linalg.norm(self._desired_pos_w - self._robot.data.root_pos_w, dim=1)
        distance_to_goal_mapped = 1 - torch.tanh(distance_to_goal / 0.8)
        grav_b = self._robot.data.projected_gravity_b
        flatness = grav_b[:, 2].abs()
        tilt_penalty = torch.square(
            torch.clamp(torch.cos(torch.deg2rad_(torch.tensor(self.cfg.tilt_limit_deg))) - flatness, min=0.0))
        v_xy = torch.linalg.vector_norm(self._robot.data.root_lin_vel_b[:, :2], dim=1)
        v_z = self._robot.data.root_lin_vel_b[:, 2]
        unsafe_ratio = torch.relu(v_xy - torch.abs(v_z))
        rewards = {
            "lin_vel": lin_vel * self.cfg.lin_vel_reward_scale * self.step_dt,
            "ang_vel": ang_vel * self.cfg.ang_vel_reward_scale * self.step_dt,
            "distance_to_goal": distance_to_goal_mapped * self.cfg.distance_to_goal_reward_scale * self.step_dt,
            "tilt_constraint": tilt_penalty * self.cfg.tilt_constraint_reward_scale * self.step_dt,
            "unsafe_velocity": unsafe_ratio * self.cfg.unsafe_velocity_reward_scale * self.step_dt,
        }
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0)
        # Logging
        for key, value in rewards.items():
            self._episode_sums[key] += value
        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        died_pos = torch.logical_or(self._robot.data.root_pos_w[:, 2] <= 0, self._robot.data.root_pos_w[:, 2] > 2.0)

        grav_b = self._robot.data.projected_gravity_b
        died_tilt = grav_b[:, 2].abs() < 0.5

        died = torch.logical_or(died_pos, died_tilt)

        return died, time_out

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._robot._ALL_INDICES

        # Logging
        final_distance_to_goal = torch.linalg.norm(
            self._desired_pos_w[env_ids] - self._robot.data.root_pos_w[env_ids], dim=1
        ).mean()
        extras = dict()
        for key in self._episode_sums.keys():
            episodic_sum_avg = torch.mean(self._episode_sums[key][env_ids])
            extras["Episode_Reward/" + key] = episodic_sum_avg / self.max_episode_length_s
            self._episode_sums[key][env_ids] = 0.0
        self.extras["log"] = dict()
        self.extras["log"].update(extras)
        extras = dict()
        extras["Episode_Termination/died"] = torch.count_nonzero(self.reset_terminated[env_ids]).item()
        extras["Episode_Termination/time_out"] = torch.count_nonzero(self.reset_time_outs[env_ids]).item()
        extras["Metrics/final_distance_to_goal"] = final_distance_to_goal.item()
        self.extras["log"].update(extras)

        num_envs_to_reset = len(env_ids)

        # Reset platform position
        random_xy = (torch.rand(num_envs_to_reset, 2,
                                device=self.device) - 0.5) * 2.0 * self.cfg.platform_spawn_range_xy
        random_z = torch.full((num_envs_to_reset, 1), self.cfg.platform_spawn_z, device=self.device)
        random_pos = torch.cat([random_xy, random_z], dim=-1)
        random_pos += self._terrain.env_origins[env_ids]
        default_root_state_platform = self._platform.data.default_root_state[env_ids]
        default_root_state_platform[:, :3] = random_pos
        random_yaw = torch.rand(num_envs_to_reset, device=self.device) * 2.0 * 3.14159
        default_root_state_platform[:, 3] = torch.cos(random_yaw / 2.0)  # w
        default_root_state_platform[:, 6] = torch.sin(random_yaw / 2.0)  # z
        self._platform.write_root_pose_to_sim(default_root_state_platform[:, :7], env_ids)
        self._platform_wheel_vel[env_ids] = 0.0

        # Set random linear velocity for the platform
        random_lin_vel_x = (torch.rand(num_envs_to_reset,
                                       device=self.device) - 0.5) * self.cfg.platform_max_linear_velocity
        random_lin_vel_y = (torch.rand(num_envs_to_reset,
                                       device=self.device) - 0.5) * self.cfg.platform_max_linear_velocity
        self._platform_target_lin_vel[env_ids, 0] = random_lin_vel_x
        self._platform_target_lin_vel[env_ids, 1] = random_lin_vel_y
        self._platform_target_lin_vel[env_ids, 2] = 0.0

        self._robot.reset(env_ids)
        super()._reset_idx(env_ids)
        if len(env_ids) == self.num_envs:
            # Spread out the resets to avoid spikes in training when many environments reset at a similar time
            self.episode_length_buf = torch.randint_like(self.episode_length_buf, high=int(self.max_episode_length))

        self._actions[env_ids] = 0.0
        self._drone_target_lin_vel_b[env_ids] = 0.0
        self._drone_target_ang_vel_b[env_ids] = 0.0

        # Sample new commands
        self._desired_pos_w[env_ids, :] = self._platform.data.root_pos_w[env_ids, :]
        # Reset robot state
        joint_pos = self._robot.data.default_joint_pos[env_ids]
        joint_vel = self._robot.data.default_joint_vel[env_ids]
        default_root_state = self._robot.data.default_root_state[env_ids]
        default_root_state[:, 2] = (torch.rand(len(env_ids), device=self.device) * (
                self.cfg.drone_max_height - self.cfg.drone_min_height) + self.cfg.drone_min_height)
        default_root_state[:, :3] += self._terrain.env_origins[env_ids]
        self._robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self._robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self._robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)

    def _set_debug_vis_impl(self, debug_vis: bool):
        # create markers if necessary for the first time
        if debug_vis:
            if not hasattr(self, "goal_pos_visualizer"):
                marker_cfg = CUBOID_MARKER_CFG.copy()
                marker_cfg.markers["cuboid"].size = (0.05, 0.05, 0.05)
                # -- goal pose
                marker_cfg.prim_path = "/Visuals/Command/goal_position"
                self.goal_pos_visualizer = VisualizationMarkers(marker_cfg)
            # set their visibility to true
            self.goal_pos_visualizer.set_visibility(True)
        else:
            if hasattr(self, "goal_pos_visualizer"):
                self.goal_pos_visualizer.set_visibility(False)

    def _debug_vis_callback(self, event):
        # update the markers
        self.goal_pos_visualizer.visualize(self._desired_pos_w)
