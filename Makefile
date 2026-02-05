all: build

install_real:
	git submodule update --init --recursive
	make -C deps/crazyflie-firmware cf2_defconfig bindings_python
	uv sync --directory src/ROS

install_sim:
	git submodule update --init --recursive
	mkdir -p deps/Alphabot2/ab2_gazebo/include
	uv sync --directory src/ROS
	
	# CrazySim
	mkdir -p deps/crazysim/crazyflie-firmware/sitl_make/build
	cmake -S deps/crazysim/crazyflie-firmware/sitl_make -B deps/crazysim/crazyflie-firmware/sitl_make/build
	export PYTHONPATH='src/ROS/.venv/lib/python3.12/site-packages' && \
		. src/ROS/.venv/bin/activate && \
		make -C deps/crazysim/crazyflie-firmware/sitl_make/build all


build: install_sim
	uv run --directory src/ROS ruff check --fix --exit-zero
	uv run --directory src/ROS ruff format
	. src/ROS/.venv/bin/activate && \
		. /opt/ros/*/setup.sh && \
		colcon --log-base .out/ros_logs build \
			--build-base .out/ros_build --install-base .out/ros_install \
			--base-paths src/ROS deps/Alphabot2 deps/crazysim/crazyswarm2_ws --cmake-args -DBUILD_TESTING=ON

sim_backend: install_sim
	export PYTHONPATH='deps/crazysim/crazyflie-firmware/build:src/ROS/.venv/lib/python3.12/site-packages' && \
	export GZ_SIM_RESOURCE_PATH="$(CURDIR)/deps/Alphabot2/ab2_gazebo/models:$$GZ_SIM_RESOURCE_PATH" && \
	. src/ROS/.venv/bin/activate && \
	. .out/ros_install/setup.sh && \
		bash deps/crazysim/crazyflie-firmware/tools/crazyflie-simulation/simulator_files/gazebo/launch/sitl_singleagent.sh -m crazyflie -x 0.5 -y 0.5

sim: build
	export PYTHONPATH='deps/crazysim/crazyflie-firmware/build:src/ROS/.venv/lib/python3.12/site-packages' && \
	. src/ROS/.venv/bin/activate && \
	. .out/ros_install/setup.sh && \
		ros2 launch crazyflie_launch simulation.launch.py

sim_carto: build
	export PYTHONPATH='deps/crazysim/crazyflie-firmware/build:src/ROS/.venv/lib/python3.12/site-packages' && \
	. src/ROS/.venv/bin/activate && \
	. .out/ros_install/setup.sh && \
		ros2 launch crazyflie_launch cartography_simulation.launch.py

teleop_drone:
	. /opt/ros/*/setup.sh && \
		ros2 run teleop_twist_keyboard teleop_twist_keyboard \
			--ros-args --remap cmd_vel:=crazyflie/input_cmd_vel

teleop_bot:
	. /opt/ros/*/setup.sh && \
		ros2 run teleop_twist_keyboard teleop_twist_keyboard \
			--ros-args --remap cmd_vel:=alphabot2/input_cmd_vel

teleop_drone_joy:
	. /opt/ros/*/setup.sh && \
		ros2 launch teleop_twist_joy teleop-launch.py \
			config_filepath:="$(CURDIR)/utils/xone.config.yaml" joy_vel:='crazyflie/input_cmd_vel'

teleop_bot_joy:
	. /opt/ros/*/setup.sh && \
		ros2 launch teleop_twist_joy teleop-launch.py \
			config_filepath:="$(CURDIR)/utils/xone.config.yaml" joy_vel:='alphabot2/input_cmd_vel'

package:
	read -p "Name: " name; \
	read -p "Description: " desc; \
	. /opt/ros/*/setup.sh && \
	ros2 pkg create --build-type ament_python \
		--maintainer-email "evan.galli@etu.univ-cotedazur.fr" --maintainer-name "Evan Galli" --license "MIT" \
		--destination-directory "./src/ROS/" --node-name "node" --description "$${desc}" "$${name}"

isaac:
	uv sync --directory src/IsaacLab
	. src/IsaacLab/.venv/bin/activate && \
		python ./utils/run_helper.py

clean:
	rm -R .out/

mr_proper: clean
	rm -R src/ROS/.venv/ src/IsaacLab/.venv/

mass_shooting:
	ps aux | grep gz | grep -v grep | awk '{print $$2}' | xargs kill -9
