import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Vector3, Transform, TransformStamped, Twist
from std_msgs.msg import Header


class Position(Node):
    def __init__(self):
        super().__init__("crazyflie_position")

        # Param
        self.declare_parameter("robot_prefix", "/crazyflie")
        robot_prefix = self.get_parameter("robot_prefix").value

        # Init
        self.position = None
        self.rotation = None

        # Subs
        self.odom_subscriber = self.create_subscription(Odometry, robot_prefix + "/odom", self.odom_subscribe_callback, 10)
        self.cmd_subscriber = self.create_subscription(Twist, "/cmd_vel", self.cmd_subscribe_callback, 10)

        # Publishers
        self.publisher_position = self.create_publisher(TransformStamped, "drone_position", 10)

        self.get_logger().info("Position node has been loaded")

    def cmd_subscribe_callback(self, msg: Twist):
        """Callback for cmd_vel subscription"""
        self.get_logger().debug("Received cmd_vel msg")

        # TODO: Recreate the odometry using the cmd_vel message

        self.get_logger().info(f"cmd_vel linear: {msg.linear}, angular: {msg.angular}")

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
