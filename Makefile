SHELL := /bin/bash

ros:
	source /opt/ros/*/setup.bash && \
	colcon --log-base .out/ros_logs build --build-base .out/ros_build --install-base .out/ros_install --base-paths deps src --cmake-args -DBUILD_TESTING=ON

sim: ros
	source .out/ros_install/setup.bash && \
	export GZ_SIM_RESOURCE_PATH="$(CURDIR)/deps/crazyflie-simulation/simulator_files/gazebo/" && \
	ros2 launch crazyflie_ros2_multiranger_bringup simple_mapper_simulation.launch.py

teleop:
	source /opt/ros/*/setup.bash && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard

clean:
	rm -R .out/
