import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster


class Alphabot2Driver:
    def init(self, webots_node, properties):
        """
        Standard Webots ROS2 driver entry point.
        """
        self.robot = webots_node.robot
        self.timestep = int(self.robot.getBasicTimeStep())

        # --- 1. Initialize Devices (Motors & Sensors) ---
        self.wheel_radius = 0.021
        self.track_width = 0.088

        self.left_motor = self.robot.getDevice("wheel_left_joint")
        self.right_motor = self.robot.getDevice("wheel_right_joint")

        # Set to velocity control mode
        self.left_motor.setPosition(float("inf"))
        self.right_motor.setPosition(float("inf"))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        self.left_sensor = self.robot.getDevice("wheel_left_joint_sensor")
        self.right_sensor = self.robot.getDevice("wheel_right_joint_sensor")
        self.left_sensor.enable(self.timestep)
        self.right_sensor.enable(self.timestep)

        # --- 2. Initialize ROS 2 Node (The Fix) ---
        # We explicitly start the node here, matching the Crazyflie example.
        rclpy.init(args=None)
        self.node = rclpy.create_node("alphabot2_driver")

        # --- 3. Create Publishers & Subscribers ---
        self.node.create_subscription(Twist, "cmd_vel", self.__cmd_vel_callback, 1)
        self.odom_publisher = self.node.create_publisher(Odometry, "odom", 1)
        self.tf_broadcaster = TransformBroadcaster(self.node)

        # --- 4. Odometry State Variables ---
        self.prev_left_pos = 0.0
        self.prev_right_pos = 0.0
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0

    def step(self):
        """
        Called at every time step of the simulation.
        """
        # CRITICAL: We must spin the node to process callbacks (like cmd_vel)
        rclpy.spin_once(self.node, timeout_sec=0)

        self.__update_odometry()

    def __cmd_vel_callback(self, msg):
        linear = msg.linear.x
        angular = msg.angular.z

        # Differential drive kinematics
        v_left = linear - (angular * self.track_width / 2.0)
        v_right = linear + (angular * self.track_width / 2.0)

        # Convert m/s to rad/s
        self.left_motor.setVelocity(v_left / self.wheel_radius)
        self.right_motor.setVelocity(v_right / self.wheel_radius)

    def __update_odometry(self):
        # 1. Read Sensors
        left_pos = self.left_sensor.getValue()
        right_pos = self.right_sensor.getValue()

        # 2. Calculate delta position
        d_left = (left_pos - self.prev_left_pos) * self.wheel_radius
        d_right = (right_pos - self.prev_right_pos) * self.wheel_radius
        self.prev_left_pos = left_pos
        self.prev_right_pos = right_pos

        # 3. Calculate distance and angle change
        distance = (d_left + d_right) / 2.0
        d_th = (d_right - d_left) / self.track_width

        # 4. Update Pose
        self.x += distance * math.cos(self.th + d_th / 2.0)
        self.y += distance * math.sin(self.th + d_th / 2.0)
        self.th += d_th

        # 5. Prepare ROS Messages
        now = self.node.get_clock().now().to_msg()

        # Simple Yaw-to-Quaternion (no need for external lib)
        qz = math.sin(self.th / 2.0)
        qw = math.cos(self.th / 2.0)

        # Publish TF
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = "odom"
        t.child_frame_id = "base_link"
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(t)

        # Publish Odom
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        # Set Twist (velocity) in odom frame (optional but good practice)
        dt = self.timestep / 1000.0
        if dt > 0:
            odom.twist.twist.linear.x = distance / dt
            odom.twist.twist.angular.z = d_th / dt

        self.odom_publisher.publish(odom)
