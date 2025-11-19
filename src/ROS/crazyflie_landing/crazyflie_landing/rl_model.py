import rclpy
from rclpy.node import Node
import onnxruntime as ort
import numpy as np
import math
from ament_index_python.packages import get_package_share_directory

# Messages ROS (Adaptez selon vos besoins)
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class RLModelNode(Node):
    def __init__(self):
        super().__init__("crazyflie_landing")

        self.declare_parameter('robot_prefix', '/crazyflie')
        self.declare_parameter('platform_prefix', '/alphabot2')
        self.declare_parameter("onnx_path", "")
        
        robot_prefix = self.get_parameter('robot_prefix').value
        platform_prefix = self.get_parameter('platform_prefix').value
        self.dt = 1 / 100  # Must be the same as during training
        self.onnx_path = self.get_parameter("onnx_path").value
        if self.onnx_path == "":
            return # Do nothing if no path provided

        self.get_logger().info(f"Loading model: {self.onnx_path}")
        self.ort_session = ort.InferenceSession(
            self.onnx_path, providers=["CPUExecutionProvider"]
        )

        # Retrieving model input/output information
        self.input_name = self.ort_session.get_inputs()[0].name
        self.input_shape = self.ort_session.get_inputs()[0].shape
        self.output_name = self.ort_session.get_outputs()[0].name
        self.output_shape = self.ort_session.get_outputs()[0].shape
        self.get_logger().info(
            f"Model loaded: {self.input_name} {self.input_shape} -> {self.output_name} {self.output_shape}"
        )

        # Subscribe to odometry of both crazyflie and platform
        self.subscriber = self.create_subscription(Odometry, robot_prefix + '/odom', self.odometry_callback, 10)
        self.subscriber = self.create_subscription(Odometry, platform_prefix + '/odom', self.target_odometry_callback, 10)

        # Publisher for action commands
        self.publisher_ = self.create_publisher(Twist, robot_prefix + '/cmd_vel', 10)

        # State variables
        self.current_pose = None
        self.current_twist = None
        self.target_pose = None

        # Timer for control loop (to ensure fixed frequency)
        self.timer = self.create_timer(self.dt, self.control_loop)

    def odometry_callback(self, msg: Odometry):
        self.current_pose = msg.pose.pose
        self.current_twist = msg.twist.twist

    def target_odometry_callback(self, msg: Odometry):
        self.target_pose = msg.pose.pose

    def _quaternion_to_euler(self, qx, qy, qz, qw):
        # retourne (roll, pitch, yaw)
        # source: conversion standard quaternion -> euler (rad)
        sinr_cosp = 2.0 * (qw * qx + qy * qz)
        cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2.0 * (qw * qy - qz * qx)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        siny_cosp = 2.0 * (qw * qz + qx * qy)
        cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    def _body_rates_to_euler_rates(self, p, q, r, roll, pitch):
        # Convertit p,q,r (body rates) en φ̇, θ̇, ψ̇ (euler rates)
        # φ̇ = p + sinφ tanθ q + cosφ tanθ r
        # θ̇ = cosφ q - sinφ r
        # ψ̇ = sinφ / cosθ q + cosφ / cosθ r
        cos_r = math.cos(roll)
        sin_r = math.sin(roll)
        cos_p = math.cos(pitch)
        sin_p = math.sin(pitch)
        # attention cos_p ~= cos(theta)
        if abs(cos_p) < 1e-6:
            cos_p = 1e-6
        phi_dot = p + sin_r * math.tan(pitch) * q + cos_r * math.tan(pitch) * r
        theta_dot = cos_r * q - sin_r * r
        psi_dot = (sin_r / cos_p) * q + (cos_r / cos_p) * r
        return phi_dot, theta_dot, psi_dot

    def _gravity_in_body(self, qx, qy, qz, qw, g=9.81):
        """
        Retourne le vecteur gravité exprimé dans le repère corps.
        Hypothèse : quaternion (qx,qy,qz,qw) représente l'orientation du corps dans le monde
        (v_world = R * v_body). On applique v_body = R^T * v_world.
        """
        x, y, z, w = qx, qy, qz, qw
        # matrice de rotation R (body -> world) construite à partir du quaternion (w,x,y,z)
        R = np.array([
            [1 - 2*(y*y + z*z),     2*(x*y - z*w),       2*(x*z + y*w)],
            [2*(x*y + z*w),         1 - 2*(x*x + z*z),   2*(y*z - x*w)],
            [2*(x*z - y*w),         2*(y*z + x*w),       1 - 2*(x*x + y*y)]
        ], dtype=float)
        # vecteur gravité dans le monde ; si votre convention est NED (z vers le bas) adaptez le signe
        g_world = np.array([0.0, 0.0, -g], dtype=float)
        # projeter dans le repère corps
        g_body = R.T.dot(g_world)
        return g_body.tolist()

    def _build_observation_vector(self):
        if self.current_pose is None or self.current_twist is None or self.target_pose is None:
            return None  # No data yet

        # lin velocities from twist
        root_lin_vel_b = [
            self.current_twist.linear.x,
            self.current_twist.linear.y,
            self.current_twist.linear.z,
        ]

        # body angular rates p,q,r from twist (rad/s)
        p = self.current_twist.angular.x
        q = self.current_twist.angular.y
        r = self.current_twist.angular.z

        # orientation -> roll, pitch, yaw
        qx = self.current_pose.orientation.x
        qy = self.current_pose.orientation.y
        qz = self.current_pose.orientation.z
        qw = self.current_pose.orientation.w
        roll, pitch, yaw = self._quaternion_to_euler(qx, qy, qz, qw)

        # convert body rates -> euler angle rates (roll_dot, pitch_dot, yaw_dot)
        roll_dot, pitch_dot, yaw_dot = self._body_rates_to_euler_rates(p, q, r, roll, pitch)
        root_ang_vel_b = [roll_dot, pitch_dot, yaw_dot]

        projected_gravity_b = self._gravity_in_body(qx, qy, qz, qw)

        desired_pos_b = [self.target_pose.position.x - self.current_pose.position.x,
                        self.target_pose.position.y - self.current_pose.position.y,
                        self.target_pose.position.z - self.current_pose.position.z]

        return np.array(
            root_lin_vel_b +
            root_ang_vel_b +
            projected_gravity_b +
            desired_pos_b
        )

    def control_loop(self):
        """Main loop: Observation -> Inference -> Action"""

        obs = self._build_observation_vector()
        if obs is None:
            return  # No sensor data yet

        self.get_logger().debug(f"Observation: {obs}")

        # Format for ONNX (Batch Size of 1)
        # Shape: [1, number_of_observations]
        input_tensor = obs.reshape(1, -1).astype(np.float32)

        # Inference (Model execution)
        outputs = self.ort_session.run(
            [self.output_name], {self.input_name: input_tensor}
        )[0][0]
        thrust, moment_x, moment_y, moment_z = outputs.astype(float).tolist()

        # Publish action
        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = thrust
        msg.angular.x = moment_x
        msg.angular.y = moment_y
        msg.angular.z = moment_z
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = RLModelNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
