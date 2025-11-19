all: ros

install:
	mkdir -p deps/Alphabot2/ab2_gazebo/include
	. /opt/ros/*/setup.sh && \
		uv venv --directory src/ROS --allow-existing

	. src/ROS/.venv/bin/activate && \
		uv sync --directory src/ROS

ros: install
	. src/ROS/.venv/bin/activate && \
	. /opt/ros/*/setup.sh && \
	colcon --log-base .out/ros_logs build --build-base .out/ros_build --install-base .out/ros_install --base-paths src/ROS deps/Alphabot2 --cmake-args -DBUILD_TESTING=ON

sim: ros
	export PYTHONPATH='src/ROS/.venv/lib/python3.12/site-packages' && \
	. src/ROS/.venv/bin/activate && \
	. .out/ros_install/setup.sh && \
	ros2 launch crazyflie_launch simulation.launch.py


teleop_drone:
	. /opt/ros/*/setup.sh && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=crazyflie/input_cmd_vel

teleop_bot:
	. /opt/ros/*/setup.sh && \
	ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=alphabot2/input_cmd_vel

teleop_drone_joy:
	. /opt/ros/*/setup.sh && \
	ros2 launch teleop_twist_joy teleop-launch.py config_filepath:="$(CURDIR)/utils/xone.config.yaml" joy_vel:='crazyflie/input_cmd_vel'

teleop_bot_joy:
	. /opt/ros/*/setup.sh && \
	ros2 launch teleop_twist_joy teleop-launch.py config_filepath:="$(CURDIR)/utils/xone.config.yaml" joy_vel:='alphabot2/input_cmd_vel'

isaac:
	python ./utils/run_helper.py

clean:
	rm -R .out/ src/ROS/.venv/
