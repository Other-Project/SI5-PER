import rclpy
from geometry_msgs.msg import Pose
from rclpy.node import Node
from ros_gz_interfaces.srv import SetEntityPose


class ResetPos(Node):
    def __init__(self):
        super().__init__("reset_pos")
        self.get_logger().info("Initializing ResetPos node (Harmonic version)...")

        self.robot_name = "crazyflie"

        service_name = "/world/empty/set_pose"
        self.client = self.create_client(SetEntityPose, service_name)

        self.subscriber = self.create_subscription(Pose, "/crazyflie/set_pose", self.reset_pos_callback, 10)

        # while not self.client.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info(f"En attente du service {service_name} (Avez-vous lancé le ros_gz_bridge ?)...")

    def reset_pos_callback(self, msg: Pose):
        self.get_logger().info("Received reset position command, calling service to teleport the robot...")

        req = SetEntityPose.Request()

        req.entity.name = self.robot_name
        req.entity.type = 2  # Type model for Gazebo

        req.pose = msg
        future = self.client.call_async(req)
        future.add_done_callback(self.callback_done)

    def callback_done(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("The service responded 'success'")
            else:
                self.get_logger().warn("The service responded 'failure'")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = ResetPos()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
