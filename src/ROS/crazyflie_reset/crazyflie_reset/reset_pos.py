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

    def reset_pos_callback(self, msg: Pose):
        self.get_logger().info("Received reset position command, calling service to teleport the robot...")

        req = SetEntityPose.Request()

        req.entity.name = self.robot_name
        req.entity.type = 2  # Type model for Gazebo

        # Add clipping to ensure the position is within reasonable bounds
        msg.position.x = max(min(msg.position.x, 5.0), -5.0)
        msg.position.y = max(min(msg.position.y, 5.0), -5.0)
        msg.position.z = min(msg.position.z, 5.0)

        req.pose = msg
        self.client.call_async(req)

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
