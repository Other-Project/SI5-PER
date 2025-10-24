SHELL := /bin/bash

ros:
	source /opt/ros/*/setup.bash && \
	colcon --log-base .out/ros_logs build --build-base .out/ros_build --install-base .out/ros_install --base-paths src/ROS --cmake-args -DBUILD_TESTING=ON

sim: ros
	source .out/ros_install/setup.bash && \
	ros2 launch crazyflie_launch simulation.launch.py

ros_term: ros
	source .out/ros_install/setup.bash && \
	bash

teleop:
	source /opt/ros/*/setup.bash && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard

clean:
	rm -R .out/
