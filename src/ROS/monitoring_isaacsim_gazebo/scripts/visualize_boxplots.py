import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore
import os

BAGS = {
    "Isaac Sim": "src/ROS/monitoring_isaacsim_gazebo/bag_isaac",
    "Gazebo": "src/ROS/monitoring_isaacsim_gazebo/bag_gazebo",
}

COLORS = {
    "Isaac Sim": "blue",
    "Gazebo": "yellow",
    "Webots": "red",
}


def read_bag(bag_path):
    altitudes = []
    velocities_3d = []

    with Reader(bag_path) as reader:
        typestore = get_typestore(Stores.ROS2_JAZZY)
        connections = [c for c in reader.connections if c.topic == "/crazyflie/odom"]
        if not connections:
            print(f"No /crazyflie/odom in {bag_path}")
            return None, None

        for connection, _, rawdata in reader.messages(connections=connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            altitudes.append(msg.pose.pose.position.z)
            vx = msg.twist.twist.linear.x
            vy = msg.twist.twist.linear.y
            vz = msg.twist.twist.linear.z
            velocities_3d.append(np.sqrt(vx**2 + vy**2 + vz**2))

    return np.array(altitudes), np.array(velocities_3d)


def main():
    all_altitudes = {}
    all_velocities = {}

    for label, bag_path in BAGS.items():
        if not os.path.exists(bag_path):
            print(f"Bag not found: {bag_path}")
            continue
        print(f"Reading {label}...")
        alt, vel = read_bag(bag_path)
        if alt is not None:
            all_altitudes[label] = alt
            all_velocities[label] = vel

    if not all_altitudes:
        print("No data found.")
        return

    labels = list(all_altitudes.keys())
    colors = [COLORS.get(l, "gray") for l in labels]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
    fig.suptitle("Distributions des Métriques de Vol dans les differentes simulations",
                 fontsize=14, fontweight='bold')

    # Altitude Plot
    bp1 = ax1.boxplot(
        [all_altitudes[l] for l in labels],
        labels=labels,
        patch_artist=True,
        showfliers=False,
        flierprops=dict(marker='o', markersize=4, alpha=0.4),
        medianprops=dict(color='black', linewidth=2),
    )
    for patch, color in zip(bp1['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.set_title("Altitude de Vol", fontsize=12)
    ax1.set_ylabel("Altitude (m)")
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0.1, 0.5)

    # Velocity Plot
    bp2 = ax2.boxplot(
        [all_velocities[l] for l in labels],
        labels=labels,
        patch_artist=True,
        notch=False,
        showfliers=False,
        flierprops=dict(marker='o', markersize=3, alpha=0.4),
        medianprops=dict(color='black', linewidth=2),
    )
    for patch, color in zip(bp2['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_title("Vitesse 3D", fontsize=12)
    ax2.set_ylabel("Vitesse (m/s)")
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output = "boxplots_comparison.png"
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"\nBoxplots saved to {output}")


if __name__ == "__main__":
    main()
