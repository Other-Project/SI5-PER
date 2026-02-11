from rosbags.rosbag2 import Reader
from rosbags.typesys import get_typestore, Stores
import numpy as np

bag_path = "../gazebo_bags/gazebo_run1"

def main():
    with Reader(bag_path) as reader:
        typestore = get_typestore(Stores.ROS2_JAZZY)
        
        drone_altitudes = []
        platform_altitudes = []
        
        crazyflie_connections = [c for c in reader.connections if c.topic == "/crazyflie/odom"]
        alphabot2_connections = [c for c in reader.connections if c.topic == "/alphabot2/odom"]
        
        if not crazyflie_connections or not alphabot2_connections:
            print("Topic /crazyflie/odom or /alphabot2/odom not found!")
            exit(1)
        
        print(f"Connections found for both topics")
        print(f"Reading messages...\n")
        
        for connection, timestamp, rawdata in reader.messages(connections=crazyflie_connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            drone_altitudes.append(msg.pose.pose.position.z)
        
        for connection, timestamp, rawdata in reader.messages(connections=alphabot2_connections):
            msg = typestore.deserialize_cdr(rawdata, connection.msgtype)
            platform_altitudes.append(msg.pose.pose.position.z)
        
        print(f"Drone altitudes: {len(drone_altitudes)}")
        print(f"Platform altitudes: {len(platform_altitudes)}")
    
    drone_altitudes = np.array(drone_altitudes)
    platform_altitudes = np.array(platform_altitudes)
    
    min_length = min(len(drone_altitudes), len(platform_altitudes))
    drone_altitudes = drone_altitudes[:min_length]
    platform_altitudes = platform_altitudes[:min_length]
    
    target_altitudes = platform_altitudes + 0.1
    
    altitude_diff = drone_altitudes - target_altitudes
    
    print(f"\n{'='*60}")
    print("Altitude Distribution Analysis")
    print(f"{'='*60}")
    print(f"\nAbsolute Altitude (drone Z position):")
    print(f"  Mean:  {np.mean(drone_altitudes):.4f} m")
    print(f"  Std:   {np.std(drone_altitudes):.4f} m")
    print(f"  Min:   {np.min(drone_altitudes):.4f} m")
    print(f"  Max:   {np.max(drone_altitudes):.4f} m")
    
    
    print(f"\nPlatform Altitude:")
    print(f"  Mean:  {np.mean(platform_altitudes):.4f} m")
    print(f"  Std:   {np.std(platform_altitudes):.4f} m")
    
    
    print(f"\nAltitude difference (distance to target = platform + 10cm):")
    print(f"  Mean:  {np.mean(altitude_diff):.4f} m")
    print(f"  Std:   {np.std(altitude_diff):.4f} m")
    print(f"  Min:   {np.min(altitude_diff):.4f} m (lowest point relative to target)")
    print(f"  Max:   {np.max(altitude_diff):.4f} m (highest point relative to target)")
    
    # if np.mean(altitude_diff) > 0:
    #     print(f"Drone flies on average {np.mean(altitude_diff)*100:.2f} cm TOO HIGH")
    # else:
    #     print(f"Drone flies on average {abs(np.mean(altitude_diff))*100:.2f} cm TOO LOW")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
