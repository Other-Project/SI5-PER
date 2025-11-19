import rclpy
from rclpy.node import Node
import onnxruntime as ort
import numpy as np
from ament_index_python.packages import get_package_share_directory
import os

# Messages ROS (Adaptez selon vos besoins)
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32MultiArray


class RLModelNode(Node):
    def __init__(self):
        super().__init__("crazyflie_landing")

        self.declare_parameter("onnx_path")
        self.onnx_path = self.get_parameter("onnx_path").value
        if not self.onnx_path:
            return # Do nothing if no path provided
        self.dt = 1 / 100  # Must be the same as during training

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
            f"Model loaded: {self.input_name} [{self.input_shape}] -> {self.output_name} [{self.output_shape}]"
        )

        # TODO: Subscribing to sensors
        # self.subscription = self.create_subscription(JointState, "/joint_states", self.listener_callback, 10)

        # Publishing commands (Actions)
        self.cmd_publisher = self.create_publisher(
            Float32MultiArray, "/robot_commands", 10
        )

        # Storing sensor data
        self.latest_joint_state = None

        # Timer for control loop (to ensure fixed frequency)
        self.timer = self.create_timer(self.dt, self.control_loop)

    def listener_callback(self, msg):
        """Updating sensor data upon reception"""
        self.latest_joint_state = msg

    def _build_observation_vector(self):
        if self.latest_joint_state is None:
            return None  # No data yet

        return np.array([])  # TODO: Replace with actual observation vector

    def control_loop(self):
        """Main loop: Observation -> Inference -> Action"""

        obs = self._build_observation_vector()
        if obs is None:
            return  # No sensor data yet

        # Format for ONNX (Batch Size of 1)
        # Shape: [1, number_of_observations]
        input_tensor = obs.reshape(1, -1).astype(np.float32)

        # Inference (Model execution)
        outputs = self.ort_session.run(
            [self.output_name], {self.input_name: input_tensor}
        )

        # Retrieve action (first element of the batch)
        action_array = outputs[0][0]

        # Publish action
        msg = Float32MultiArray()
        msg.data = action_array.tolist()
        self.cmd_publisher.publish(msg)


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
