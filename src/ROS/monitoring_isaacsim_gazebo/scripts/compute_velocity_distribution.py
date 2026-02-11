import numpy as np
from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore

bag_path = "../gazebo_bags/gazebo_run1"


def main():
    with Reader(bag_path) as reader:
        typestore = get_typestore(Stores.ROS2_JAZZY)

        crazyflie_velocities = []

        crazyflie_velocities_connection = [c for c in reader.connections if c.topic == "/crazyflie/odom"]

        if not crazyflie_velocities_connection:
            print("Topic /crazyflie/odom not found !")
            exit(1)

        print("Connection found for /crazyflie/odom")
        print("Reading messages...\n")

        for connection, timestamp, rawdata in reader.messages(connections=crazyflie_velocities_connection):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            crazyflie_velocities.append([msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z])

        print(f"Crazyflie velocities: {len(crazyflie_velocities)}")

    np_crazyflie_velocities = np.array(crazyflie_velocities)
    horizontal_xy_crazyflie_velocities = np.linalg.norm(np_crazyflie_velocities[:, :2], axis=1)
    vertical_z_crazyflie_velocities = np_crazyflie_velocities[:, 2]
    xyz_crazyflie_velocities = np.linalg.norm(np_crazyflie_velocities, axis=1)

    print(f"\n{'=' * 60}")
    print("Velocity Distribution Analysis")
    print(f"{'=' * 60}")
    print("\nHorizontal (XY tracking):")
    print(f"  Mean:  {np.mean(horizontal_xy_crazyflie_velocities):.4f} m/s")
    print(f"  Std:   {np.std(horizontal_xy_crazyflie_velocities):.4f} m/s")
    print(f"  Max:   {np.max(horizontal_xy_crazyflie_velocities):.4f} m/s")

    print("\nVertical (Z descent):")
    print(f"  Mean:  {np.mean(vertical_z_crazyflie_velocities):.4f} m/s")
    print(f"  Std:   {np.std(vertical_z_crazyflie_velocities):.4f} m/s")

    print("\n3D Total:")
    print(f"  Mean:  {np.mean(xyz_crazyflie_velocities):.4f} m/s")
    print(f"  Std:   {np.std(xyz_crazyflie_velocities):.4f} m/s")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
