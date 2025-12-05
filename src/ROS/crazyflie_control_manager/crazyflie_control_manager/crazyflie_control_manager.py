import rclpy
from lifecycle_msgs.msg import State, Transition
from rclpy.node import Node
from std_msgs.msg import Bool

from .lifecycle_manager import LifecycleManager


class ControlManager(Node):
    def __init__(self):
        super().__init__("crazyflie_control_manager")
        self.landing_manager = LifecycleManager("rl_model")

        self.create_subscription(Bool, "/crazyflie/land", self.land_callback, 10)

        self.landing_manager.set_state(Transition.TRANSITION_ACTIVATE)

    def land_callback(self, msg: Bool):
        state = self.landing_manager.get_state()
        if msg.data and state.id == State.PRIMARY_STATE_INACTIVE:
            self.landing_manager.set_state(Transition.TRANSITION_ACTIVATE)
        elif not msg.data and state.id == State.PRIMARY_STATE_ACTIVE:
            self.landing_manager.set_state(Transition.TRANSITION_DEACTIVATE)
        elif state.id in (State.PRIMARY_STATE_INACTIVE, State.PRIMARY_STATE_ACTIVE):
            pass  # No transition needed
        else:
            self.get_logger().error(f"Invalid state transition requested (land={msg.data}), current state: {state.label} [{state.id}]")


def main(args=None):
    rclpy.init(args=args)
    node = ControlManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
