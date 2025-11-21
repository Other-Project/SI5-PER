# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import isaaclab.sim as sim_utils
import torch
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass

# Import your AlphaBot config
from ....assets import ALPHABOT_CFG, ALPHABOT_JOINTS_NAMES, ACTUATORS_LEFT_WHEEL, ACTUATORS_RIGHT_WHEEL


@configclass
class AlphaBotTestEnvCfg(DirectRLEnvCfg):
    """Configuration for AlphaBot test environment."""

    # Environment settings
    episode_length_s = 20.0
    decimation = 2
    action_space = 2
    observation_space = 13
    state_space = 0
    debug_vis = True

    # Simulation
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

    # Terrain - FIXED collision settings
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=0,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=True,
    )

    # Scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=16,
        env_spacing=3.0,
        replicate_physics=True,
        clone_in_fabric=True
    )

    # AlphaBot platform
    platform: ArticulationCfg = ALPHABOT_CFG.replace(
        prim_path="/World/envs/env_.*/Platform"
    )

    # Spawn settings
    platform_spawn_z = 0.1
    platform_spawn_range_xy = 1.0


class AlphaBotTestEnv(DirectRLEnv):
    """Test environment with only the AlphaBot platform."""

    cfg: AlphaBotTestEnvCfg

    def __init__(self, cfg: AlphaBotTestEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self._actions = torch.zeros(
            self.num_envs,
            self.cfg.action_space,
            device=self.device
        )

        wheel_joint_names = [
            ALPHABOT_JOINTS_NAMES[ACTUATORS_LEFT_WHEEL],
            ALPHABOT_JOINTS_NAMES[ACTUATORS_RIGHT_WHEEL]
        ]
        self._platform_joint_indices = self._platform.find_joints(wheel_joint_names)[0]

        self._episode_sums = {
            "action_rate": torch.zeros(self.num_envs, dtype=torch.float, device=self.device),
        }

    def _setup_scene(self):
        """Setup the scene with platform and terrain."""
        self._platform = Articulation(self.cfg.platform)
        self.scene.articulations["platform"] = self._platform

        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)

        self.scene.clone_environments(copy_from_source=False)

        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])

        # Add lights
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor):
        """Process actions before physics step."""
        self._actions = actions.clone().clamp(-1.0, 1.0)

    def _apply_action(self):
        """Apply wheel velocity commands to the platform."""
        max_wheel_vel = 10.0
        wheel_velocities = self._actions * max_wheel_vel

        self._platform.set_joint_velocity_target(
            wheel_velocities,
            joint_ids=self._platform_joint_indices
        )

    def _get_observations(self) -> dict:
        """Get platform state as observations."""
        obs = torch.cat(
            [
                self._platform.data.root_pos_w,
                self._platform.data.root_quat_w,
                self._platform.data.root_lin_vel_b,
                self._platform.data.root_ang_vel_b,
            ],
            dim=-1,
        )
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        """Simple reward: penalize large actions."""
        action_rate = torch.sum(torch.square(self._actions), dim=1)
        reward = -0.01 * action_rate * self.step_dt

        self._episode_sums["action_rate"] += -reward

        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Check termination conditions."""
        time_out = self.episode_length_buf >= self.max_episode_length - 1

        platform_z = self._platform.data.root_pos_w[:, 2]
        platform_quat = self._platform.data.root_quat_w

        roll = torch.atan2(
            2.0 * (platform_quat[:, 0] * platform_quat[:, 1] + platform_quat[:, 2] * platform_quat[:, 3]),
            1.0 - 2.0 * (platform_quat[:, 1] ** 2 + platform_quat[:, 2] ** 2)
        )
        pitch = torch.asin(
            2.0 * (platform_quat[:, 0] * platform_quat[:, 2] - platform_quat[:, 3] * platform_quat[:, 1]))

        died = torch.logical_or(
            torch.logical_or(torch.abs(roll) > 1.0, torch.abs(pitch) > 1.0),
            platform_z < -0.1
        )

        return died, time_out

    def _reset_idx(self, env_ids: torch.Tensor | None):
        """Reset specified environments."""
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._platform._ALL_INDICES

        # Logging
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
        self.extras["log"].update(extras)

        num_envs_to_reset = len(env_ids)

        # Reset platform position - spawn above ground with random XY position
        random_xy = (torch.rand(num_envs_to_reset, 2,
                                device=self.device) - 0.5) * 2.0 * self.cfg.platform_spawn_range_xy
        random_z = torch.full((num_envs_to_reset, 1), self.cfg.platform_spawn_z, device=self.device)
        random_pos = torch.cat([random_xy, random_z], dim=-1)
        random_pos += self._terrain.env_origins[env_ids]

        # Get default state and set new position
        default_root_state = self._platform.data.default_root_state[env_ids].clone()
        default_root_state[:, :3] = random_pos

        # Random yaw orientation
        random_yaw = torch.rand(num_envs_to_reset, device=self.device) * 2.0 * 3.14159
        default_root_state[:, 3] = torch.cos(random_yaw / 2.0)  # w
        default_root_state[:, 4] = 0.0  # x
        default_root_state[:, 5] = 0.0  # y
        default_root_state[:, 6] = torch.sin(random_yaw / 2.0)  # z

        # Reset all velocities to zero
        default_root_state[:, 7:13] = 0.0

        # Write pose and velocity to simulation
        self._platform.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self._platform.write_root_velocity_to_sim(default_root_state[:, 7:13], env_ids)

        # Reset joint states
        joint_pos = self._platform.data.default_joint_pos[env_ids]
        joint_vel = self._platform.data.default_joint_vel[env_ids]
        self._platform.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)

        # Reset actions
        self._actions[env_ids] = 0.0

        # Call parent reset
        super()._reset_idx(env_ids)

        # Randomize reset timing to avoid synchronized resets
        if len(env_ids) == self.num_envs:
            self.episode_length_buf = torch.randint_like(
                self.episode_length_buf,
                high=int(self.max_episode_length)
            )
