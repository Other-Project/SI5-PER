import numpy as np
import onnxruntime as ort
import rclpy
from geometry_msgs.msg import Point, Quaternion, Twist, Vector3
from nav_msgs.msg import Odometry
from rclpy.node import Node


class RLModelNode(Node):
    def __init__(self):
        super().__init__("crazyflie_landing")

        self.declare_parameter("robot_prefix", "/crazyflie")
        self.declare_parameter("platform_prefix", "/alphabot2")
        self.declare_parameter("onnx_path", "")

        robot_prefix = self.get_parameter("robot_prefix").value
        platform_prefix = self.get_parameter("platform_prefix").value
        self.dt = 1 / 100  # Must be the same as during training
        self.onnx_path = self.get_parameter("onnx_path").value
        if self.onnx_path == "":
            return  # Do nothing if no path provided

        self.get_logger().info(f"Loading model: {self.onnx_path}")
        self.ort_session = ort.InferenceSession(self.onnx_path, providers=["CPUExecutionProvider"])

        # Retrieving model input/output information
        self.input_name = self.ort_session.get_inputs()[0].name
        self.input_shape = self.ort_session.get_inputs()[0].shape
        self.output_name = self.ort_session.get_outputs()[0].name
        self.output_shape = self.ort_session.get_outputs()[0].shape
        self.get_logger().info(f"Model loaded: {self.input_name} {self.input_shape} -> {self.output_name} {self.output_shape}")

        # Subscribe to odometry of both crazyflie and platform
        self.subscriber = self.create_subscription(Odometry, robot_prefix + "/odom", self.odometry_callback, 10)
        self.subscriber = self.create_subscription(Odometry, platform_prefix + "/odom", self.target_odometry_callback, 10)

        # Publisher for action commands
        self.publisher_ = self.create_publisher(Twist, robot_prefix + "/cmd_vel", 10)

        # State variables
        self.current_pose = None
        self.current_twist = None
        self.target_pose = None

        # Timer for control loop (to ensure fixed frequency)
        self.timer = self.create_timer(self.dt, self.control_loop, autostart=False)
        self.tmp = self.create_timer(0.1, self.wait)  # TODO: Remove this

    def wait(self):
        self.timer.reset()
        self.tmp.cancel()

    def odometry_callback(self, msg: Odometry):
        self.current_pose = msg.pose.pose
        self.current_twist = msg.twist.twist

    def target_odometry_callback(self, msg: Odometry):
        self.target_pose = msg.pose.pose

    def vectToNumpy(self, vec: Vector3 | Point) -> np.ndarray:
        return np.array([vec.x, vec.y, vec.z])

    def quaternionToNumpy(self, quat: Quaternion) -> np.ndarray:
        return np.array([quat.w, quat.x, quat.y, quat.z])

    def _build_observation_vector(self):
        if self.current_pose is None or self.current_twist is None or self.target_pose is None:
            return None  # No data yet

        drone_lin_vel_b = self.vectToNumpy(self.current_twist.linear)
        drone_pos_w = self.vectToNumpy(self.current_pose.position)
        drone_quat_w = self.quaternionToNumpy(self.current_pose.orientation)
        target_pos_w = self.vectToNumpy(self.target_pose.position)
        target_pos_w[2] += 0.1  # Target slightly above platform
        desired_pos_b = target_pos_w - drone_pos_w

        return np.concatenate([drone_lin_vel_b, drone_quat_w, desired_pos_b])

    def control_loop(self):
        """Main loop: Observation -> Inference -> Action"""

        obs = self._build_observation_vector()
        if obs is None:
            return  # No sensor data yet

        self.get_logger().debug(f"Observation: {obs}")

        # Format for ONNX (Batch Size of 1)
        # Shape: [1, number_of_observations]
        input_tensor = obs.reshape(1, -1).astype(np.float32)
        self.get_logger().info(f"Input: {np.array_str(input_tensor, precision=3, suppress_small=True)}")

        # Inference (Model execution)
        outputs = self.ort_session.run([self.output_name], {self.input_name: input_tensor})[0][0]
        self.get_logger().info(f"Outputs: {np.array_str(outputs, precision=3, suppress_small=True)}")

        velocity_x, velocity_y, velocity_z, angular_velocity_z = outputs.clip(-1.0, 1.0)
        factor = 0.2
        max_val = max(abs(velocity_z) * factor, factor)
        velocity_x = np.clip(velocity_x, -max_val, max_val)
        velocity_y = np.clip(velocity_y, -max_val, max_val)
        angular_velocity_z = np.clip(angular_velocity_z, -max_val, max_val)

        self.get_logger().info(
            f"Commanded velocities -> vx: {velocity_x:.3f}, vy: {velocity_y:.3f}, vz: {velocity_z:.3f}, wz: {angular_velocity_z:.3f}"
        )

        # Publish action
        msg = Twist()
        msg.linear.x = float(velocity_x * 0.5)
        msg.linear.y = float(velocity_y * 0.5)
        msg.linear.z = float(velocity_z * 0.5)
        msg.angular.x = 0.0  # ignored
        msg.angular.y = 0.0  # ignored
        msg.angular.z = float(angular_velocity_z * 0.4)
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
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
