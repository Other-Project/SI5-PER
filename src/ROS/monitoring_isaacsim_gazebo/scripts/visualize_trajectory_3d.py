import argparse
import sys
import os

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
    parser = argparse.ArgumentParser(description="Visualize and compare 3D trajectories (Gazebo vs Webots).")
    parser.add_argument("--gazebo", type=str, help="Path to Gazebo .npz file")
    parser.add_argument("--webots", type=str, help="Path to Webots .npz file")
    args = parser.parse_args()

    files_map = {}
    if args.gazebo:
        files_map["Gazebo"] = args.gazebo
    if args.webots:
        files_map["Webots"] = args.webots
    
    if not files_map:
        default_gazebo = "../.out/metrics/gazebo_trajectory.npz"
        default_webots = "../.out/metrics/webots_trajectory.npz"
        if os.path.exists(default_gazebo): files_map["Gazebo"] = default_gazebo
        if os.path.exists(default_webots): files_map["Webots"] = default_webots

    if not files_map:
        print("No files provided and defaults not found.")
        print("Usage: python3 visualize_trajectory_3d.py --gazebo <file> --webots <file>")
        sys.exit(1)

    print(f"Visualizing: {list(files_map.keys())}")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    
    ax.set_title(f"Trajectory Comparison: {' vs '.join(files_map.keys())}", fontsize=14)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")

    colors = {"Gazebo": "orange", "Webots": "red"}
    styles = {"Gazebo": "-", "Webots": "-"}

    all_x = []
    all_y = []
    all_z = []

    for name, path in files_map.items():
        data = load_data(path)
        if not data: continue
            
        drone_pos = data["drone"]
        platform_pos = data["platform"]
        
        color = colors.get(name, "green")
        style = styles.get(name, "-")
        
        # Plot Drone
        ax.plot(drone_pos[:, 0], drone_pos[:, 1], drone_pos[:, 2], 
                label=f"{name} Drone", color=color, linestyle=style, linewidth=1.5, alpha=0.9)
        
        # Start/End markers
        ax.scatter(drone_pos[0, 0], drone_pos[0, 1], drone_pos[0, 2], 
                   color=color, marker="o", facecolors="none", s=30)
        ax.scatter(drone_pos[-1, 0], drone_pos[-1, 1], drone_pos[-1, 2], 
                   color=color, marker="x", s=50)

        # Plot Platform
        #TODO: plot both platform to check the departure point
        ax.plot(platform_pos[:, 0], platform_pos[:, 1], platform_pos[:, 2],
                label=f"{name} Platform", color=color, linestyle="--", linewidth=1, alpha=0.5)

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
    
    output_img = "trajectory_comparison_3d.png"
    plt.savefig(output_img)
    print(f"Plot saved to {output_img}")
    # plt.show() 

if __name__ == "__main__":
    main()
