import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PointStamped

import tf_transformations
import numpy as np

class Position(Node):
    def __init__(self):
        super().__init__('crazyflie_position')

        # Param
        self.declare_parameter('robot_prefix', '/crazyflie')
        robot_prefix = self.get_parameter('robot_prefix').value

        # Init
        self.position = [0.0, 0.0, 0.0]
        self.angles = [0.0, 0.0, 0.0]

        # Subs
        self.odom_subscriber = self.create_subscription(Odometry, robot_prefix + '/odom', self.odom_subscribe_callback, 10)

        # Publishers
        self.publisher_position = self.create_publisher(PointStamped, 'drone_position', 10)

        self.get_logger().info(f"Simple mapper set for crazyflie " + robot_prefix +
                               f" using the odom and scan topic")
        
    def odom_subscribe_callback(self, msg: Odometry):
        self.position[0] = msg.pose.pose.position.x
        self.position[1] = msg.pose.pose.position.y
        self.position[2] = msg.pose.pose.position.z
        q = msg.pose.pose.orientation
        """euler = tf_transformations.euler_from_quaternion([q.x, q.y, q.z, q.w])
        self.angles[0] = euler[0]
        self.angles[1] = euler[1]
        self.angles[2] = euler[2]"""
        
        self.get_logger().info(f"Received odom msg pos={self.position} and angles={self.angles}")
        self.send_pos(msg)

    def send_pos(self, msg: Odometry):
        out = PointStamped()
        out.header = msg.header
        out.point = msg.pose.pose.position
        print(f"Received odom message {msg}, sending {out}")
        self.publisher_position.publish(out)

    

def main(args=None):
    rclpy.init(args=args)
    position = Position()
    rclpy.spin(position)
    rclpy.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()