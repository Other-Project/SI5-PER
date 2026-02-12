import numpy as np
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore

bag_path = "../gazebo_bags/gazebo_run1"
target_height = 0.1


def main():
    with Reader(bag_path) as reader:
        typestore = get_typestore(Stores.ROS2_JAZZY)

        drone_positions = []
        platform_positions = []

        crazyflie_odom_connections = [c for c in reader.connections if c.topic == "/crazyflie/odom"]
        alphabot2_odom_connections = [c for c in reader.connections if c.topic == "/alphabot2/odom"]

        if not crazyflie_odom_connections or not alphabot2_odom_connections:
            print("Topic /crazyflie/odom or /alphabot2/odom not found !")
            exit(1)

        print("Connection found for /crazyflie/odom")
        print("Reading messages...\n")

        for connection, timestamp, rawdata in reader.messages(connections=crazyflie_odom_connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            drone_positions.append([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])

        for connection, timestamp, rawdata in reader.messages(connections=alphabot2_odom_connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            platform_positions.append([msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z])

        print(f"Drone positions length : {len(drone_positions)}")
        print(f"Platform positions length : {len(platform_positions)}")

    np_drone_positions = np.array(drone_positions)
    np_platform_positions = np.array(platform_positions)
    print(f"\nDrone positions shape : {np_drone_positions.shape}")
    print(f"Platform positions shape : {np_platform_positions.shape}")

    min_length = min(len(np_drone_positions), len(np_platform_positions))

    np_drone_positions = np_drone_positions[:min_length]
    np_platform_positions = np_platform_positions[:min_length]
    print(f"\nDrone positions shape : {np_drone_positions.shape}")
    print(f"Platform positions shape : {np_platform_positions.shape}")

    target_positions = np_platform_positions.copy()
    target_positions[:, 2] += target_height
    print(f"\nTarget positions shape : {target_positions.shape}")

    distances = np.linalg.norm(np_drone_positions - target_positions, axis=1)
    print(f"\nDistances shape : {distances.shape}")
    print(f"Distances : {distances}")

    print(f"\n{'=' * 60}")
    print("Distance to the moving platform")
    print(f"{'=' * 60}")
    print(f"  Mean Distance Error:  {np.mean(distances):.4f} m")
    print(f"  Max Distance Error:   {np.max(distances):.4f} m")
    print(f"  Min Distance Error:   {np.min(distances):.4f} m")
    print(f"  Std Deviation:        {np.std(distances):.4f} m")
    print(f"{'=' * 60}")

    output_file = "../.out/metrics/gazebo_trajectory.npz"
    np.savez(
        output_file,
        drone_positions=np_drone_positions,
        platform_positions=np_platform_positions,
        target_positions=target_positions,
        distances=distances,
    )
    print(f"\n Trajectory data saved to: {output_file}")
    print(f"  - Drone positions: {np_drone_positions.shape}")
    print(f"  - Platform positions: {np_platform_positions.shape}")
    print(f"  - Target positions: {target_positions.shape}")

    print("   1. Record a bag in the others simulator")
    print("   2. Relaunch this script with the new bag")
    print("   3. Compare the Mean Distance Error !")
    print("   4. Use saved trajectories for 3D visualization")


if __name__ == "__main__":
    main()
