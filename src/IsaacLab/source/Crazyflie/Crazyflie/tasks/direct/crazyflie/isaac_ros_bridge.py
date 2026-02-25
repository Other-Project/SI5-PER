import torch
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry
from rclpy.node import Node


class IsaacRosBridge(Node):
    """
    ROS 2 Node to bridge between Isaac and ROS for the Crazyflie environment.
    """

    def __init__(self, topic_cmd="/crazyflie/input_cmd_vel", reset_pub="/crazyflie/set_pose",
                 topic_odom="/crazyflie/odom"):
        super().__init__("isaac_ros_bridge_node")

        self.cmd_pub = self.create_publisher(Twist, topic_cmd, 10)
        self.reset_pub = self.create_publisher(Pose, reset_pub, 10)

        self.drone_odom_pub = self.create_publisher(Odometry, "/isaac/crazyflie/odom", 10)
        self.platform_odom_pub = self.create_publisher(Odometry, "/isaac/alphabot/odom", 10)

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

    def publish_reset_pos(self, pos, quat):
        msg = Pose()
        msg.position.x = float(pos[0])
        msg.position.y = float(pos[1])
        msg.position.z = float(pos[2])

        msg.orientation.w = float(quat[0])
        msg.orientation.x = float(quat[1])
        msg.orientation.y = float(quat[2])
        msg.orientation.z = float(quat[3])

        self.reset_pub.publish(msg)
        print(f"[ROS Bridge] Published reset position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    def publish_command(self, lin_vel, ang_vel_z):
        msg = Twist()
        msg.linear.x = float(lin_vel[0])
        msg.linear.y = float(lin_vel[1])
        msg.linear.z = float(lin_vel[2])
        msg.angular.z = float(ang_vel_z)
        self.cmd_pub.publish(msg)

    def publish_simulation_state(self, drone_pos, drone_quat, drone_lin_vel, drone_ang_vel,
                                 plat_pos, plat_quat, plat_lin_vel, plat_ang_vel):
        now = self.get_clock().now().to_msg()

        drone_msg = Odometry()
        drone_msg.header.stamp = now
        drone_msg.header.frame_id = "world"
        drone_msg.child_frame_id = "crazyflie_base_link"

        drone_msg.pose.pose.position.x = float(drone_pos[0])
        drone_msg.pose.pose.position.y = float(drone_pos[1])
        drone_msg.pose.pose.position.z = float(drone_pos[2])
        drone_msg.pose.pose.orientation.w = float(drone_quat[0])
        drone_msg.pose.pose.orientation.x = float(drone_quat[1])
        drone_msg.pose.pose.orientation.y = float(drone_quat[2])
        drone_msg.pose.pose.orientation.z = float(drone_quat[3])

        drone_msg.twist.twist.linear.x = float(drone_lin_vel[0])
        drone_msg.twist.twist.linear.y = float(drone_lin_vel[1])
        drone_msg.twist.twist.linear.z = float(drone_lin_vel[2])
        drone_msg.twist.twist.angular.x = float(drone_ang_vel[0])
        drone_msg.twist.twist.angular.y = float(drone_ang_vel[1])
        drone_msg.twist.twist.angular.z = float(drone_ang_vel[2])

        self.drone_odom_pub.publish(drone_msg)

        plat_msg = Odometry()
        plat_msg.header.stamp = now
        plat_msg.header.frame_id = "world"
        plat_msg.child_frame_id = "alphabot_base_link"

        plat_msg.pose.pose.position.x = float(plat_pos[0])
        plat_msg.pose.pose.position.y = float(plat_pos[1])
        plat_msg.pose.pose.position.z = float(plat_pos[2])
        plat_msg.pose.pose.orientation.w = float(plat_quat[0])
        plat_msg.pose.pose.orientation.x = float(plat_quat[1])
        plat_msg.pose.pose.orientation.y = float(plat_quat[2])
        plat_msg.pose.pose.orientation.z = float(plat_quat[3])

        plat_msg.twist.twist.linear.x = float(plat_lin_vel[0])
        plat_msg.twist.twist.linear.y = float(plat_lin_vel[1])
        plat_msg.twist.twist.linear.z = float(plat_lin_vel[2])
        plat_msg.twist.twist.angular.x = float(plat_ang_vel[0])
        plat_msg.twist.twist.angular.y = float(plat_ang_vel[1])
        plat_msg.twist.twist.angular.z = float(plat_ang_vel[2])

        self.platform_odom_pub.publish(plat_msg)
