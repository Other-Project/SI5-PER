import rclpy
from geometry_msgs.msg import Transform, TransformStamped, Vector3
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Header


class Position(Node):
    def __init__(self):
        super().__init__("alphabot2_position")

        # Param
        self.declare_parameter("robot_prefix", "/alphabot2")
        robot_prefix = self.get_parameter("robot_prefix").value

        # Init
        self.position = None
        self.rotation = None

        # Subs
        self.odom_subscriber = self.create_subscription(Odometry, robot_prefix + "/odometry", self.odom_subscribe_callback, 10)

        # Publishers
        self.publisher_position = self.create_publisher(TransformStamped, "robot_position", 10)

        self.get_logger().info("Position node has been loaded")

    def odom_subscribe_callback(self, msg: Odometry):
        """Callback for odometry subscription"""
        self.get_logger().debug("Received odometry msg")
        self.position = msg.pose.pose.position
        self.rotation = msg.pose.pose.orientation
        self.send_transform()

    def send_transform(self):
        header = Header(stamp=self.get_clock().now().to_msg(), frame_id="world")
        out = TransformStamped(header=header)
        vect = Vector3(x=self.position.x, y=self.position.y, z=self.position.z)
        out.transform = Transform(translation=vect, rotation=self.rotation)
        self.get_logger().debug("Sending transform msg")
        self.publisher_position.publish(out)


def main(args=None):
    rclpy.init(args=args)
    position = Position()
    rclpy.spin(position)
    position.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
