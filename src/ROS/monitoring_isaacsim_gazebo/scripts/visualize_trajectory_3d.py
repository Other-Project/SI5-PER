import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def load_data(path):
    if not os.path.exists(path):
        print(f"Warning: File {path} not found.")
        return None
    data = np.load(path)
    return {
        "drone": data["drone_positions"],
        "platform": data["platform_positions"],
        "target": data["target_positions"]
    }

def main():
    parser = argparse.ArgumentParser(description="Visualize and compare 3D trajectories (Gazebo vs Webots vs Isaac).")
    parser.add_argument("--gazebo", type=str, help="Path to Gazebo .npz file")
    parser.add_argument("--webots", type=str, help="Path to Webots .npz file")
    parser.add_argument("--isaac", type=str, help="Path to Isaac Sim .npz file")
    args = parser.parse_args()

    files_map = {}
    if args.gazebo:
        files_map["Gazebo"] = args.gazebo
    if args.webots:
        files_map["Webots"] = args.webots
    if args.isaac:
        files_map["Isaac"] = args.isaac
    
    # Defaults if nothing provided
    if not files_map:
        default_gazebo = "src/ROS/monitoring_isaacsim_gazebo/.out/metrics/gazebo_trajectory.npz"
        default_webots = "src/ROS/monitoring_isaacsim_gazebo/.out/metrics/webots_trajectory.npz"
        default_isaac = "src/ROS/monitoring_isaacsim_gazebo/.out/metrics/isaac_trajectory.npz"
        if os.path.exists(default_gazebo): files_map["Gazebo"] = default_gazebo
        if os.path.exists(default_webots): files_map["Webots"] = default_webots
        if os.path.exists(default_isaac): files_map["Isaac Sim"] = default_isaac

    if not files_map:
        print("No files provided and defaults not found.")
        print("Usage: python3 visualize_trajectory_3d.py --gazebo <file> --webots <file> --isaac <file>")
        sys.exit(1)

    print(f"Visualizing: {list(files_map.keys())}")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    colors = {"Gazebo": "yellow", "Webots": "red", "Isaac Sim": "blue"}
    
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
            label=f"{label} Drone",
            color=colors.get(label, "black"),
            linewidth=2,
        )
        
        # Plot Start/End markers
        ax.scatter(
            drone_pos[0, 0], drone_pos[0, 1], drone_pos[0, 2],
            color=colors.get(label, "black"), marker="o", s=50, label=f"{label} Start"
        )
        ax.scatter(
            drone_pos[-1, 0], drone_pos[-1, 1], drone_pos[-1, 2],
            color=colors.get(label, "black"), marker="x", s=50, label=f"{label} End"
        )

        ax.plot(
            platform_pos[:, 0],
            platform_pos[:, 1],
            platform_pos[:, 2],
            label=f"{label} Platform",
            color=colors.get(label, "black"),
            linestyle="--",
            alpha=0.5
        )
        
        all_x.extend(drone_pos[:, 0])
        all_y.extend(drone_pos[:, 1])
        all_z.extend(drone_pos[:, 2])

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("3D Trajectory Comparison (Gazebo vs Webots vs Isaac)")
    
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
    
    output_img = "trajectory_comparison_3d.png"
    plt.savefig(output_img)
    print(f"Plot saved to {output_img}")
    # plt.show() 

if __name__ == "__main__":
    main()
