import rclpy
from crazyflie_py import Crazyswarm
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class ControlServices(Node):
    def __init__(self, cf):
        super().__init__("control_services")
        self.declare_parameter("hover_height", 0.5)
        self.declare_parameter("robot_prefix", "/crazyflie")
        self.declare_parameter("incoming_twist_topic", "/crazyflie/input_cmd_vel")
        self.declare_parameter("max_ang_z_rate", 0.4)

        hover_height = self.get_parameter("hover_height").value
        robot_prefix = self.get_parameter("robot_prefix").value
        incoming_twist_topic = self.get_parameter("incoming_twist_topic").value
        max_ang_z_rate = self.get_parameter("max_ang_z_rate").value

        self.cf = cf

        self.current_pose = None
        self.is_flying = False
        self.takeoff_height = hover_height
        self.max_ang_z_rate = max_ang_z_rate
        self.teleop_cmd = Twist()

        self.create_subscription(Odometry, robot_prefix + "/odom", self.odometry_callback, 10)
        self.create_subscription(Twist, incoming_twist_topic, self.cmd_vel_callback, 10)
        self.timer = self.create_timer(0.01, self.timer_callback)  # 100Hz for smooth control

    def timer_callback(self):
        msg = self.teleop_cmd
        if self.current_pose is None:
            return

        # Takeoff logic
        if not self.is_flying and msg.linear.z > 0.1:
            self.cf.takeoff(targetHeight=self.takeoff_height, duration=2.0)
            self.is_flying = True
            self.get_logger().info("Takeoff command sent via crazyswarm2")
            return

        # Landing logic
        if self.is_flying and msg.linear.z < -0.1 and self.current_pose.position.z < 0.15:
            self.cf.land(targetHeight=0.04, duration=2.0)
            self.is_flying = False
            self.get_logger().info("Landing command sent via crazyswarm2")
            return

        # Velocity control (only if flying)
        if self.is_flying:
            vx = float(msg.linear.x)
            vy = float(msg.linear.y)
            vz = float(msg.linear.z)
            yaw_rate = float(max(min(msg.angular.z, self.max_ang_z_rate), -self.max_ang_z_rate))
            self.cf.cmdVelocityWorld(vx=vx, vy=vy, vz=vz, yawRate=yaw_rate)

    def odometry_callback(self, msg):
        self.current_pose = msg.pose.pose

    def cmd_vel_callback(self, msg):
        self.teleop_cmd = msg


def main(args=None):
    swarm = Crazyswarm()
    cf = swarm.allcfs.crazyflies[0]
    node = ControlServices(cf)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
