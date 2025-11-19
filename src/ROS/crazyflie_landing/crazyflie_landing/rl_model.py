import rclpy
from rclpy.node import Node
import onnxruntime as ort
import numpy as np
from .utils import angular_vel, gravity_in_body
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


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
        self.subscriber = self.create_subscription(
            Odometry, robot_prefix + "/odom", self.odometry_callback, 10
        )
        self.subscriber = self.create_subscription(
            Odometry, platform_prefix + "/odom", self.target_odometry_callback, 10
        )

        # Publisher for action commands
        self.publisher_ = self.create_publisher(Twist, robot_prefix + "/cmd_vel", 10)

        # State variables
        self.current_pose = None
        self.current_twist = None
        self.target_pose = None

        # Timer for control loop (to ensure fixed frequency)
        self.timer = self.create_timer(self.dt, self.control_loop, autostart=False)
        self.tmp = self.create_timer(40.0, self.wait)

    def wait(self):
        self.timer.reset()
        self.tmp.cancel()

    def odometry_callback(self, msg: Odometry):
        self.current_pose = msg.pose.pose
        self.current_twist = msg.twist.twist

    def target_odometry_callback(self, msg: Odometry):
        self.target_pose = msg.pose.pose

    def _build_observation_vector(self):
        if (
            self.current_pose is None
            or self.current_twist is None
            or self.target_pose is None
        ):
            return None  # No data yet

        root_lin_vel_b = [
            self.current_twist.linear.x,
            self.current_twist.linear.y,
            self.current_twist.linear.z,
        ]
        root_ang_vel_b = angular_vel(
            self.current_pose.orientation, self.current_twist.angular
        )
        projected_gravity_b = gravity_in_body(self.current_pose.orientation)
        desired_pos_b = [
            self.target_pose.position.x - self.current_pose.position.x,
            self.target_pose.position.y - self.current_pose.position.y,
            self.target_pose.position.z - self.current_pose.position.z,
        ]

        return np.array(
            root_lin_vel_b + root_ang_vel_b + projected_gravity_b + desired_pos_b
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
