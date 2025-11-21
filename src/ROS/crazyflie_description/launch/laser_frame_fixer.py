"""
Node to fix the LaserScan frame_id from Gazebo.
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
        self.subscription = self.create_subscription(LaserScan, "/crazyflie/scan", self.scan_callback, 10)

        # Publish corrected scan
        self.publisher = self.create_publisher(LaserScan, "/crazyflie/scan_corrected", 10)

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
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
