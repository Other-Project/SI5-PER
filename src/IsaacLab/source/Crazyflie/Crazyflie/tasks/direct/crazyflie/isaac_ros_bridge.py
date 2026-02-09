import torch
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class IsaacRosBridge(Node):
    """
    ROS 2 Node to bridge between Isaac and ROS for the Crazyflie environment.
    """

    def __init__(self, topic_cmd="/crazyflie/input_cmd_vel", topic_odom="/crazyflie/odom"):
        super().__init__("isaac_ros_bridge_node")

        self.cmd_pub = self.create_publisher(Twist, topic_cmd, 10)

        self.odom_sub = self.create_subscription(Odometry, topic_odom, self.odom_callback, 10)

        self.latest_pos = None
        self.latest_quat = None
        self.latest_lin_vel = None
        self.latest_ang_vel = None
        self.received_first_msg = False

    def odom_callback(self, msg: Odometry):
        print("[ROS Bridge] Received Odom message from Gazebo")
        print(
            f"Position: ({msg.pose.pose.position.x:.2f}, {msg.pose.pose.position.y:.2f}, {msg.pose.pose.position.z:.2f})")

        self.latest_pos = torch.tensor([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ], dtype=torch.float32)

        self.latest_quat = torch.tensor([
            msg.pose.pose.orientation.w,
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z
        ], dtype=torch.float32)

        self.latest_lin_vel = torch.tensor([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ], dtype=torch.float32)

        self.latest_ang_vel = torch.tensor([
            msg.twist.twist.angular.x,
            msg.twist.twist.angular.y,
            msg.twist.twist.angular.z
        ], dtype=torch.float32)

        self.received_first_msg = True

    def publish_command(self, lin_vel, ang_vel_z):
        msg = Twist()
        msg.linear.x = float(lin_vel[0])
        msg.linear.y = float(lin_vel[1])
        msg.linear.z = float(lin_vel[2])
        msg.angular.z = float(ang_vel_z)
        self.cmd_pub.publish(msg)
