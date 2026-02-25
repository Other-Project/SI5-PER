import math
from enum import Enum, auto

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class Status(Enum):
    ON_LAND = auto()
    TAKEOFF = auto()
    FLYING = auto()
    LANDING = auto()


class ControlServices(Node):
    def __init__(self):
        super().__init__("control_services")

        # Declare and retrieve parameters
        self.declare_parameter("robot_prefix", "/crazyflie")
        self.declare_parameter("incoming_twist_topic", "/crazyflie/input_cmd_vel")
        self.declare_parameter("max_linear", 0.1)
        self.declare_parameter("max_ang_z_rate", 0.05)
        self.declare_parameter("height_hold_gain", 1.0)
        self.declare_parameter("flying_threshold", 0.2)
        self.declare_parameter("max_height", 3.0)
        self.declare_parameter("safe_takeoff_height", 0.4)

        robot_prefix = self.get_parameter("robot_prefix").value
        incoming_topic = self.get_parameter("incoming_twist_topic").value
        self.max_linear = self.get_parameter("max_linear").value
        self.max_ang_z = self.get_parameter("max_ang_z_rate").value
        self.kp_z = self.get_parameter("height_hold_gain").value
        self.fly_threshold = self.get_parameter("flying_threshold").value
        self.max_height = self.get_parameter("max_height").value
        self.safe_takeoff_height = self.get_parameter("safe_takeoff_height").value

        # Setup communication
        self.cmd_pub = self.create_publisher(Twist, f"{robot_prefix}/cmd_vel", 10)
        self.odom_sub = self.create_subscription(Odometry, f"{robot_prefix}/odom", self.odom_cb, 10)
        self.cmd_sub = self.create_subscription(Twist, incoming_topic, self.cmd_cb, 10)
        self.control_timer = self.create_timer(1 / 50, self.control_loop)

        # Initialize variables
        self.status = None  # Status will be initialized on first Odometry message
        self.current_pos = None
        self.desired_z = 0.0
        self.input_cmd = Twist()

        self.get_logger().info("Control Services: Waiting for Odometry...")

    def odom_cb(self, msg: Odometry):
        init = self.current_pos is None
        self.current_pos = msg.pose.pose.position

        # Detect startup state (ground or mid-air)
        if init:
            if self.current_pos.z > self.safe_takeoff_height:
                self.status = Status.FLYING
                self.desired_z = self.current_pos.z
                self.get_logger().info(f"Startup Mid-Air ({self.current_pos.z:.2f}m). Status: FLYING.")
            else:
                self.status = Status.ON_LAND
                self.get_logger().info("Startup on Ground. Status: ON_LAND.")

    def cmd_cb(self, msg: Twist):
        self.input_cmd = msg

    def control_loop(self):
        if self.current_pos is None or self.status is None:
            return

        out_msg = Twist()
        user_z = self.input_cmd.linear.z
        tolerance = 1e-2

        # --- State Machine Transitions & Behaviors ---

        if self.status == Status.ON_LAND:
            # Takeoff detection
            if user_z > 0.4:
                self.get_logger().info("Takeoff command received -> Switch to TAKEOFF")
                self.status = Status.TAKEOFF
            else:
                self.cmd_pub.publish(Twist())  # Cut/idle motors
                return

        elif self.status == Status.TAKEOFF:
            if self.current_pos.z >= self.safe_takeoff_height:
                self.get_logger().info("Safe takeoff height reached -> Switch to FLYING")
                self.status = Status.FLYING
                self.desired_z = self.current_pos.z
            else:
                # Automated takeoff behavior (ignore user inputs, go straight up)
                out_msg.linear.z = 0.5

        elif self.status == Status.FLYING:
            # Landing detection
            if user_z < -0.4 and self.current_pos.z < self.fly_threshold:
                self.get_logger().info("Landing condition met -> Switch to LANDING")
                self.status = Status.LANDING
            else:
                # Pass through XY/Yaw commands
                out_msg.linear.x = self.input_cmd.linear.x
                out_msg.linear.y = self.input_cmd.linear.y
                out_msg.angular.x = self.input_cmd.angular.x
                out_msg.angular.y = self.input_cmd.angular.y
                out_msg.angular.z = self.input_cmd.angular.z

                # Ceiling limit
                if user_z > 0 and self.current_pos.z > self.max_height:
                    user_z = 0.0

                # Z-axis control: manual or height hold
                if abs(user_z) > tolerance:
                    out_msg.linear.z = user_z
                    self.desired_z = self.current_pos.z
                else:
                    error = self.desired_z - self.current_pos.z
                    out_msg.linear.z = error * self.kp_z

        elif self.status == Status.LANDING:
            if self.current_pos.z < 0.01:
                self.get_logger().info("Ground contact detected -> Switch to ON_LAND")
                self.status = Status.ON_LAND
                self.cmd_pub.publish(Twist())  # Cut motors immediately
                return
            else:
                # Automated landing behavior (ignore user inputs, go straight down safely)
                out_msg.linear.z = -0.3

        # --- Output Clipping (Applies during TAKEOFF, FLYING, and LANDING) ---
        xy_mag = math.hypot(out_msg.linear.x, out_msg.linear.y)
        if xy_mag > self.max_linear:
            scale = self.max_linear / xy_mag
            out_msg.linear.x *= scale
            out_msg.linear.y *= scale

        out_msg.linear.z = max(min(out_msg.linear.z, 1.0), -0.5)
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
