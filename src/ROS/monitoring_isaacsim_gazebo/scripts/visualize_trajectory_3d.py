import os

import matplotlib.pyplot as plt
import numpy as np

gazebo_trajectory_path = "../.out/metrics/gazebo_trajectory.npz"


def main():
    if not os.path.exists(gazebo_trajectory_path):
        print(f"Error: The file {gazebo_trajectory_path} does not exist.")
        print("Make sure to run compute_distance_to_goal.py first to generate the data.")
        exit(1)

    print(f"Loading data from {gazebo_trajectory_path}...")

    data = np.load(gazebo_trajectory_path)
    drone_pos = data["drone_positions"]
    platform_pos = data["platform_positions"]
    target_pos = data["target_positions"]

    print(f"Points loaded: {len(drone_pos)}")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_title("Gazebo trajectory : Drone vs Platform", fontsize=14)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")

    all_x = np.concatenate((drone_pos[:, 0], platform_pos[:, 0]))
    all_y = np.concatenate((drone_pos[:, 1], platform_pos[:, 1]))
    all_z = np.concatenate((drone_pos[:, 2], platform_pos[:, 2]))

    max_range = np.array([all_x.max() - all_x.min(), all_y.max() - all_y.min(), all_z.max() - all_z.min()]).max() / 2.0

    mid_x = (all_x.max() + all_x.min()) * 0.5
    mid_y = (all_y.max() + all_y.min()) * 0.5
    mid_z = (all_z.max() + all_z.min()) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.plot(drone_pos[:, 0], drone_pos[:, 1], drone_pos[:, 2], label="Crazyflie", color="blue", linewidth=1, alpha=0.8)
    ax.scatter(drone_pos[0, 0], drone_pos[0, 1], drone_pos[0, 2], color="blue", marker="o", facecolors="none", label="departure")

    ax.plot(
        platform_pos[:, 0],
        platform_pos[:, 1],
        platform_pos[:, 2],
        label="AlphaBot2",
        color="red",
        linestyle="--",
        linewidth=3,
        marker=".",
        markersize=2,
        alpha=0.6,
    )
    ax.scatter(drone_pos[-1, 0], drone_pos[-1, 1], drone_pos[-1, 2], color="blue", marker="o", label="arrival")

    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
