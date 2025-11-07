SHELL := /bin/bash

ros:
	mkdir -p deps/Alphabot2/ab2_gazebo/include
	source /opt/ros/*/setup.bash && \
	colcon --log-base .out/ros_logs build --build-base .out/ros_build --install-base .out/ros_install --base-paths src/ROS deps/Alphabot2 --cmake-args -DBUILD_TESTING=ON

sim: ros
	source .out/ros_install/setup.bash && \
	ros2 launch crazyflie_launch simulation.launch.py

ros_term: ros
	source .out/ros_install/setup.bash && \
	bash

teleop_drone:
	source /opt/ros/*/setup.bash && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard

teleop_bot:
	source /opt/ros/*/setup.bash && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=alphabot2/cmd_vel

teleop_drone_joy:
	source /opt/ros/*/setup.bash && \
	ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox'

clean:
	rm -R .out/
