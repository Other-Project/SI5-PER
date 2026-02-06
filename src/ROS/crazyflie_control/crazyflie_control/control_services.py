import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class ControlServices(Node):
    def __init__(self):
        super().__init__("control_services")

        # Declare and retrieve parameters
        self.declare_parameter("robot_prefix", "/crazyflie")
        self.declare_parameter("incoming_twist_topic", "/crazyflie/input_cmd_vel")
        self.declare_parameter("max_linear", 0.5)
        self.declare_parameter("max_ang_z_rate", 0.4)
        self.declare_parameter("height_hold_gain", 1.0)
        self.declare_parameter("flying_threshold", 0.1)

        robot_prefix = self.get_parameter("robot_prefix").value
        incoming_topic = self.get_parameter("incoming_twist_topic").value
        self.max_linear = self.get_parameter("max_linear").value
        self.max_ang_z = self.get_parameter("max_ang_z_rate").value
        self.kp_z = self.get_parameter("height_hold_gain").value
        self.fly_threshold = self.get_parameter("flying_threshold").value

        # Setup communication
        self.cmd_pub = self.create_publisher(Twist, f"{robot_prefix}/cmd_vel", 10)
        self.odom_sub = self.create_subscription(Odometry, f"{robot_prefix}/odom", self.odom_cb, 10)
        self.cmd_sub = self.create_subscription(Twist, incoming_topic, self.cmd_cb, 10)
        self.timer = self.create_timer(0.1, self.control_loop)

        # Initialize variables
        self.is_flying = False
        self.current_pos = None
        self.desired_z = 0.0
        self.input_cmd = Twist()

        self.get_logger().info("Control Services: Waiting for Odometry...")

    def odom_cb(self, msg: Odometry):
        init = self.current_pos is None
        self.current_pos = msg.pose.pose.position

        # Detect startup state (ground or mid-air)
        if init:
            if self.current_pos.z > self.fly_threshold:
                self.is_flying = True
                self.desired_z = self.current_pos.z
                self.get_logger().info(f"Startup Mid-Air ({self.current_pos.z:.2f}m). Engaging Height Hold.")
            else:
                self.is_flying = False
                self.get_logger().info("Startup on Ground. System IDLE.")

    def cmd_cb(self, msg: Twist):
        self.input_cmd = msg

    def control_loop(self):
        if self.current_pos is None:
            return

        out_msg = Twist()
        user_z = self.input_cmd.linear.z
        tolerance = 1e-2

        if not self.is_flying:
            # Takeoff detection
            if user_z > 0:
                self.get_logger().info("Takeoff detected -> Switch to FLYING")
                self.is_flying = True
                self.desired_z = self.current_pos.z
                out_msg.linear.z = user_z
        else:
            # Pass through XY/Yaw commands
            out_msg.linear.x = self.input_cmd.linear.x
            out_msg.linear.y = self.input_cmd.linear.y
            out_msg.angular.x = self.input_cmd.angular.x
            out_msg.angular.y = self.input_cmd.angular.y
            out_msg.angular.z = self.input_cmd.angular.z

            # Landing detection
            if user_z < 0 and self.current_pos.z < self.fly_threshold:
                self.get_logger().info("Landing detected -> Switch to IDLE")
                self.is_flying = False
                self.cmd_pub.publish(Twist())  # Cut motors
                return

            # Z-axis control: manual or height hold
            if abs(user_z) > tolerance:
                out_msg.linear.z = user_z
                self.desired_z = self.current_pos.z
            else:
                error = self.desired_z - self.current_pos.z
                out_msg.linear.z = error * self.kp_z

        # Clip outputs
        xy_mag = math.hypot(out_msg.linear.x, out_msg.linear.y)  # Clip by magnitude to preserves direction
        if xy_mag > self.max_linear:
            scale = self.max_linear / xy_mag
            out_msg.linear.x *= scale
            out_msg.linear.y *= scale
        out_msg.linear.z = self.clamp(out_msg.linear.z, self.max_linear)
        out_msg.angular.x = 0.0
        out_msg.angular.y = 0.0
        out_msg.angular.z = self.clamp(out_msg.angular.z, self.max_ang_z)

        self.cmd_pub.publish(out_msg)

    def clamp(self, value, limit):
        return max(min(value, limit), -limit)


def main(args=None):
    rclpy.init(args=args)
    node = ControlServices()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
