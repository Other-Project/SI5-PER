#!/usr/bin/env python3
"""
Node to fix the LaserScan frame_id from Gazebo.
Subscribes to raw scan data and publishes with corrected frame_id.
Gazebo publishes frame_id as 'crazyflie/base_footprint/lidar_sensor'
but the actual TF frame is 'crazyflie/lidar_sensor'
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LaserFrameFixer(Node):
    def __init__(self):
        super().__init__("laser_frame_fixer")

        # Subscribe to the raw scan from bridge
        self.subscription = self.create_subscription(LaserScan, "/crazyflie/scan_raw", self.scan_callback, 10)

        # Publish corrected scan on standard topic
        self.publisher = self.create_publisher(LaserScan, "/crazyflie/scan", 10)

        self.get_logger().info("Laser frame fixer started")

    def scan_callback(self, msg: LaserScan):
        """Fix the frame_id and republish"""
        # Correct the frame_id
        msg.header.frame_id = "crazyflie/lidar_sensor"

        # Republish
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LaserFrameFixer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
