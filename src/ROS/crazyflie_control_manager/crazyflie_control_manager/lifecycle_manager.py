import rclpy
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import ChangeState, GetState
from rclpy.node import Node


class LifecycleManager(Node):
    def __init__(self, target_node_name):
        super().__init__("lifecycle_manager")
        self.logger = self.get_logger()
        self.target_node = target_node_name

        # Clients for lifecycle services
        self._client_get_state = self.create_client(GetState, f"/{self.target_node}/get_state")
        self._client_change_state = self.create_client(ChangeState, f"/{self.target_node}/change_state")

    def set_state(self, transition_id) -> ChangeState.Response:
        """Sends a request to change the state of the target node."""
        if not self._client_change_state.wait_for_service(timeout_sec=5.0):
            self.logger.error(f"Could not find node {self.target_node}")
            return

        req = ChangeState.Request()
        req.transition.id = transition_id
        self.logger.info(f"Requesting transition {transition_id} for node {self.target_node}")
        try:
            future = self._client_change_state.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            return future.result()
        except Exception as e:
            self.logger.error(f"Failed to change state for node {self.target_node}: {e}")

    def get_state(self) -> State:
        """Queries the current state of the target node."""
        if not self._client_get_state.wait_for_service(timeout_sec=5.0):
            self.logger.error(f"Could not find node {self.target_node}")
            return

        req = GetState.Request()
        try:
            future = self._client_get_state.call_async(req)
            rclpy.spin_until_future_complete(self, future)
            res: GetState.Response = future.result()
            return res.current_state
        except Exception as e:
            self.logger.error(f"Failed to get state for node {self.target_node}: {e}")
