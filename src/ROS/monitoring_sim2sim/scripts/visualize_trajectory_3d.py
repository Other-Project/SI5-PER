import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="Visualize and compare 3D trajectories (Gazebo vs Webots vs Isaac Sim).")
    parser.add_argument("--gazebo", type=str, help="Path to Gazebo .npz file")
    parser.add_argument("--webots", type=str, help="Path to Webots .npz file")
    parser.add_argument("--isaac", type=str, help="Path to Isaac Sim .npz file")
    args = parser.parse_args()

    files_map = {}
    if args.isaac:
        files_map["Isaac Sim"] = args.isaac
    if args.gazebo:
        files_map["Gazebo"] = args.gazebo
    if args.webots:
        files_map["Webots"] = args.webots

    if not files_map:
        default_gazebo = "src/ROS/monitoring_sim2sim/.out/metrics/gazebo_trajectory.npz"
        default_webots = "src/ROS/monitoring_sim2sim/.out/metrics/webots_trajectory.npz"
        default_isaac = "src/ROS/monitoring_sim2sim/.out/metrics/isaac_trajectory.npz"
        if os.path.exists(default_gazebo):
            files_map["Gazebo"] = default_gazebo
        if os.path.exists(default_webots):
            files_map["Webots"] = default_webots
        if os.path.exists(default_isaac):
            files_map["Isaac Sim"] = default_isaac

    if not files_map:
        print("No files provided and defaults not found.")
        print("Usage: python3 visualize_trajectory_3d.py --gazebo <file> --webots <file> --isaac <file>")
        sys.exit(1)

    print(f"Visualizing: {list(files_map.keys())}")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("3D Trajectory Comparison (Gazebo vs Webots vs Isaac Sim)")

    colors = {"Gazebo": "#FFB000", "Webots": "#DC267F", "Isaac Sim": "#785EF0"}
    styles = {"Gazebo": "-", "Webots": "-", "Isaac Sim": "-"}

    all_x = []
    all_y = []
    all_z = []

    for label, file_path in files_map.items():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        data = np.load(file_path)
        drone_pos = data["drone_positions"]
        platform_pos = data["platform_positions"]

        if len(drone_pos) == 0:
            print(f"Empty data in {file_path}")
            continue

        # Plot Drone Trajectory
        ax.plot(
            drone_pos[:, 0],
            drone_pos[:, 1],
            drone_pos[:, 2],
            label=f"{label}",
            color=colors.get(label, "green"),
            linestyle=styles.get(label, "-"),
            linewidth=1.5,
            alpha=0.9,
        )

        # Start/End markers
        ax.scatter(drone_pos[0, 0], drone_pos[0, 1], drone_pos[0, 2], color=colors.get(label, "green"), marker="o", facecolors="none", s=30)
        ax.scatter(drone_pos[-1, 0], drone_pos[-1, 1], drone_pos[-1, 2], color=colors.get(label, "green"), marker="x", s=50)

        # Platform trajectory
        ax.plot(
            platform_pos[:, 0],
            platform_pos[:, 1],
            platform_pos[:, 2],
            label=f"{label} Platform",
            color=colors.get(label, "green"),
            linestyle="--",
            alpha=0.5,
        )

        all_x.extend(drone_pos[:, 0])
        all_y.extend(drone_pos[:, 1])
        all_z.extend(drone_pos[:, 2])

    if all_x:
        all_x = np.array(all_x)
        all_y = np.array(all_y)
        all_z = np.array(all_z)

        max_range = np.array([all_x.max() - all_x.min(), all_y.max() - all_y.min(), all_z.max() - all_z.min()]).max() / 2.0
        mid_x = (all_x.max() + all_x.min()) * 0.5
        mid_y = (all_y.max() + all_y.min()) * 0.5
        mid_z = (all_z.max() + all_z.min()) * 0.5

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.legend()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", ".out", "graph")
    os.makedirs(output_dir, exist_ok=True)
    output_img = os.path.join(output_dir, "trajectory_comparison_3d.png")

    plt.savefig(output_img, bbox_inches="tight")
    print(f"Plot saved to {output_img}")


if __name__ == "__main__":
    main()
