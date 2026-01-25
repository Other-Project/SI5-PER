#!/bin/bash

# Run this script as root

cd project/deps/alphabot2-ros2/
export PYTHONPATH='.venv/lib/python3.12/site-packages'
. .venv/bin/activate
. install/setup.sh
export ROS_DOMAIN_ID=1
ros2 launch alphabot2 alphabot2_launch.py
