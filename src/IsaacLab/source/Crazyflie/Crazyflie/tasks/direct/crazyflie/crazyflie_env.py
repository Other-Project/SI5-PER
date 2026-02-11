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
from isaaclab.utils.math import subtract_frame_transforms, quat_apply, quat_apply_inverse
##
# Pre-defined configs
##
from isaaclab_assets import CRAZYFLIE_CFG  # isort: skip

from ....assets import JACKAL_CFG, JACKAL_JOINTS_NAMES, JACKAL_ACTUATORS_LEFT_WHEEL, JACKAL_ACTUATORS_RIGHT_WHEEL

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
    test = False

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

    # velocity command limits
    max_linear_velocity = 0.5  # m/s
    max_angular_velocity_z = 1.0  # rad/s

    # tilt constraint
    tilt_limit_deg = 80.0
    
    # P-gains (Force generation)
    gain_vel_xy = 2.0 
    gain_vel_z = 5.0
    
    # P-gains (Torque generation)
    gain_att_xy = 0.04
    gain_att_z = 0.01
    
    # D-gains for angular damping
    gain_ang_vel_xy = 0.001
    gain_ang_vel_z = 0.0003

    # Physical Limits
    max_thrust_force = 0.6
    max_torque = 0.006

    # alpha bot
    platform: ArticulationCfg = JACKAL_CFG.replace(
        prim_path="/World/envs/env_.*/Platform"
    )

    # reward scales
    lin_vel_reward_scale = -0.05
    ang_vel_reward_scale = -0.01
    distance_to_goal_reward_scale = 15.0
    tilt_constraint_penalty_scale = -5.0
    height_penalty_scale = -5.0
    landing_reward_scale = 200.0
    landing_penalty_scale = -10.0
    action_penalty_scale = -0.01
    
    landing_height_threshold = 0.15 
    landing_radius = 0.5 

    # random pose range
    platform_spawn_range_xy = 4.0
    platform_spawn_z = 0.0

    # Alpha bot movement parameters
    platform_max_linear_velocity = 0.3  # m/s
    platform_max_angular_velocity = 1.0  # rad/s

    # Curriculum learning parameters
    curriculum_length_steps = 2400
    curriculum_easy_height = 0.2
    curriculum_hard_height = 3.0

class CrazyflieEnv(DirectRLEnv):
    cfg: CrazyflieEnvCfg

    def __init__(self, cfg: CrazyflieEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Velocity commands
        self._actions = torch.zeros(self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device)
        self._drone_target_lin_vel_b = torch.zeros(self.num_envs, 3, device=self.device)
        self._drone_target_ang_vel_b = torch.zeros(self.num_envs, 3, device=self.device)

        # Platform wheel velocities for differential drive
        self._platform_wheel_vel = self._platform_wheel_vel = torch.zeros(self.num_envs, device=self.device)
        self._platform_joint_indices = None

        # Platform target velocities (linear and angular)
        self._platform_target_lin_vel = torch.rand(self.num_envs, 3, device=self.device)

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
                "height_penalty",
                "landing_reward",
                "action_penalty"
            ]
        }
        # Get specific body indices
        self._body_id = self._robot.find_bodies("body")[0]
        self._robot_mass = self._robot.root_physx_view.get_masses()[0].sum()
        self._gravity_magnitude = torch.tensor(self.sim.cfg.gravity, device=self.device).norm()
        self._robot_weight = (self._robot_mass * self._gravity_magnitude).item()

        # Initialize platform joint indices and velocities
        wheel_joint_names = [
            JACKAL_JOINTS_NAMES[JACKAL_ACTUATORS_LEFT_WHEEL],
            JACKAL_JOINTS_NAMES[JACKAL_ACTUATORS_RIGHT_WHEEL]
        ]

        # add handle for debug visualization (this is set to a valid handle inside set_debug_vis)
        self.set_debug_vis(self.cfg.debug_vis)

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self._platform = Articulation(self.cfg.platform)
        self.scene.articulations["robot"] = self._robot
        self.scene.articulations["platform"] = self._platform
        self.landing_target_view = self._platform
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
        
        target_v_x, target_v_y, target_v_z = self._drone_target_lin_vel_b[:, :3].unbind(dim=-1)
        target_yaw_rate = self._drone_target_ang_vel_b[:, 2]

        # Current State
        root_quat = self._robot.data.root_quat_w
        root_vel_w = self._robot.data.root_lin_vel_w
        root_ang_vel_b = self._robot.data.root_ang_vel_b
        mass = self._robot_mass
        
        # Velocity Controller
        vel_b = quat_apply_inverse(root_quat, root_vel_w)
        
        error_v_x = target_v_x - vel_b[:, 0]
        error_v_y = target_v_y - vel_b[:, 1]
        error_v_z = target_v_z - vel_b[:, 2]

        acc_x = error_v_x * self.cfg.gain_vel_xy
        acc_y = error_v_y * self.cfg.gain_vel_xy
        acc_z = error_v_z * self.cfg.gain_vel_z

        acc_b = torch.stack([acc_x, acc_y, acc_z], dim=-1)
        acc_w = quat_apply(root_quat, acc_b)
        
        total_force_w = acc_w * mass
        thrust_command = self._actions[:, 2] 
        total_force_w[:, 2] += mass * 9.81 * torch.clamp(thrust_command + 1.0, min=0.0, max=1.0)

        # Attitude Controller
        z_axis_b = torch.zeros_like(total_force_w)
        z_axis_b[:, 2] = 1.0
        current_z_w = quat_apply(root_quat, z_axis_b)
        
        force_magnitude = torch.norm(total_force_w, dim=1, keepdim=True)
        force_magnitude = torch.clamp(force_magnitude, min=1e-6) 
        desired_z_w = total_force_w / force_magnitude

        # Orientation Error
        rotation_error_w = torch.linalg.cross(current_z_w, desired_z_w)
        rotation_error_b = quat_apply_inverse(root_quat, rotation_error_w)

        thrust_val = torch.sum(total_force_w * current_z_w, dim=1, keepdim=True)
        thrust_val = torch.clamp(thrust_val, 0.0, self.cfg.max_thrust_force)
        
        torque_x = self.cfg.gain_att_xy * rotation_error_b[:, 0] - self.cfg.gain_ang_vel_xy * root_ang_vel_b[:, 0]
        torque_y = self.cfg.gain_att_xy * rotation_error_b[:, 1] - self.cfg.gain_ang_vel_xy * root_ang_vel_b[:, 1]
        
        yaw_error = target_yaw_rate - root_ang_vel_b[:, 2]
        torque_z = self.cfg.gain_ang_vel_z * yaw_error

        torques = torch.stack([torque_x, torque_y, torque_z], dim=-1)
        torques = torch.clamp(torques, -self.cfg.max_torque, self.cfg.max_torque)
        
        forces = torch.zeros_like(torques)
        forces[:, 2] = thrust_val.squeeze()
        
        forces_w = quat_apply(root_quat, forces)
        torques_w = quat_apply(root_quat, torques)

        self._robot.set_external_force_and_torque(
            forces=forces_w.unsqueeze(1),
            torques=torques_w.unsqueeze(1),
            body_ids=self._body_id
        )

        # Apply platform control
        root_vel = torch.zeros(self.num_envs, 6, device=self.device)
        root_vel[:, :3] = self._platform_target_lin_vel
        self._platform.write_root_velocity_to_sim(root_vel)

    def _get_observations(self) -> dict:
        self._desired_pos_w = self.landing_target_view.data.root_pos_w + torch.tensor([0.0, 0.0, 0.05], device=self.device)
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
        target_pos_w = self._desired_pos_w.clone()
        
        root_pos_w = self._robot.data.root_pos_w
        root_lin_vel_b = self._robot.data.root_lin_vel_b
        root_ang_vel_b = self._robot.data.root_ang_vel_b
        thrust_action = self._actions[:, 2] 
        
        lin_vel = torch.sum(torch.square(root_lin_vel_b), dim=1)
        ang_vel = torch.sum(torch.square(root_ang_vel_b), dim=1)
        
        distance_to_goal = torch.linalg.norm(target_pos_w - root_pos_w, dim=1)
        
        distance_to_goal_mapped = 1.0 / (1.0 + torch.square(distance_to_goal / 0.5))

        grav_b = self._robot.data.projected_gravity_b
        flatness = grav_b[:, 2].abs()
        tilt_penalty = torch.square(
            torch.clamp(torch.cos(torch.deg2rad_(torch.tensor(self.cfg.tilt_limit_deg))) - flatness, min=0.0))

        horizontal_dist = torch.linalg.norm(root_pos_w[:, :2] - target_pos_w[:, :2], dim=1)
        on_top_of_target = horizontal_dist < self.cfg.landing_radius
        height_error = root_pos_w[:, 2] - target_pos_w[:, 2]
        height_penalty = height_error * on_top_of_target.float()
        
        is_at_landing_height = torch.abs(height_error) < self.cfg.landing_height_threshold
        is_aligned = horizontal_dist < (self.cfg.landing_radius / 2.0)
        is_motors_off = thrust_action < -0.95
        landing_reward = (is_at_landing_height & is_aligned & is_motors_off).float()
        
        thrust_magnitude = torch.square(self._actions[:, 2] + 1.0)
        action_penalty = thrust_magnitude * self.cfg.action_penalty_scale * self.step_dt
        
        rewards = {
            "lin_vel": lin_vel * self.cfg.lin_vel_reward_scale * self.step_dt,
            "ang_vel": ang_vel * self.cfg.ang_vel_reward_scale * self.step_dt,
            "distance_to_goal": distance_to_goal_mapped * self.cfg.distance_to_goal_reward_scale * self.step_dt,
            "tilt_constraint": tilt_penalty * self.cfg.tilt_constraint_penalty_scale * self.step_dt, 
            "height_penalty": height_penalty * self.cfg.height_penalty_scale * self.step_dt,
            "landing_reward": landing_reward * self.cfg.landing_reward_scale * self.step_dt,
            "action_penalty": action_penalty * self.cfg.action_penalty_scale * self.step_dt,
        }
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0)
        # Logging
        for key, value in rewards.items():
            self._episode_sums[key] += value 
        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        died_pos = torch.logical_or(self._robot.data.root_pos_w[:, 2] <= 0.05, self._robot.data.root_pos_w[:, 2] > 4.0)

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
        random_xy = torch.zeros(num_envs_to_reset, 2, device=self.device)
        random_z = torch.full((num_envs_to_reset, 1), self.cfg.platform_spawn_z, device=self.device)
        random_pos = torch.cat([random_xy, random_z], dim=-1)
        random_pos += self._terrain.env_origins[env_ids]
        
        default_root_state_platform = self._platform.data.default_root_state[env_ids]
        default_root_state_platform[:, :3] = random_pos
        random_yaw = torch.rand(num_envs_to_reset, device=self.device) * 3.14159
        default_root_state_platform[:, 3] = torch.cos(random_yaw)  # w
        default_root_state_platform[:, 6] = torch.sin(random_yaw)  # z
        self._platform.write_root_pose_to_sim(default_root_state_platform[:, :7], env_ids)
        self._platform.write_root_velocity_to_sim(torch.zeros(num_envs_to_reset, 6, device=self.device), env_ids)
        self._platform_wheel_vel[env_ids] = 0.0

        curr_factor = 1.0 if self.cfg.test else min(self.common_step_counter / self.cfg.curriculum_length_steps, 1.0)
        
        vel_scale = max(0.0, (curr_factor - 0.5) * 2.0)

        random_lin_vel = torch.zeros(num_envs_to_reset, 2, device=self.device).uniform_(
            -self.cfg.platform_max_linear_velocity,
            self.cfg.platform_max_linear_velocity
        )
        self._platform_target_lin_vel[env_ids, :2] = random_lin_vel * vel_scale
        
        self._platform_target_lin_vel[env_ids, 0] = random_lin_vel[:, 0]
        self._platform_target_lin_vel[env_ids, 1] = random_lin_vel[:, 1]
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
        self._desired_pos_w[env_ids, :] = random_pos
        # Reset robot state
        joint_pos = self._robot.data.default_joint_pos[env_ids]
        joint_vel = self._robot.data.default_joint_vel[env_ids]
        
        default_root_state = self._robot.data.default_root_state[env_ids].clone()
        
        max_steps = self.cfg.curriculum_length_steps
        curriculum_factor = min(self.common_step_counter / max_steps, 1.0)
        
        platform_z_location = self.cfg.platform_spawn_z 
        
        min_spawn_z = platform_z_location + self.cfg.curriculum_easy_height
        
        max_spawn_z_offset = self.cfg.curriculum_hard_height
        current_max_z = min_spawn_z + curriculum_factor * (max_spawn_z_offset - self.cfg.curriculum_easy_height)
        
        default_root_state[:, 2].uniform_(min_spawn_z, current_max_z)
    
        platform_new_pos_w = random_pos 
        
        easy_radius = 0.0
        hard_radius = self.cfg.platform_spawn_range_xy
        current_radius = easy_radius + curriculum_factor * (hard_radius - easy_radius)
        
        noise_xy = torch.zeros(len(env_ids), 2, device=self.device)
        noise_xy.uniform_(-current_radius, current_radius)
        
        default_root_state[:, 0] = platform_new_pos_w[:, 0] + noise_xy[:, 0]
        default_root_state[:, 1] = platform_new_pos_w[:, 1] + noise_xy[:, 1]
        
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
