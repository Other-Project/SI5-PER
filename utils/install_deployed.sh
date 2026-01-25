#!/bin/bash

# -----------------------------
#
# These instructions are for Ubuntu Server 24.04
#
# -----------------------------

# Setup services
sudo systemctl mask systemd-networkd-wait-online.service
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# Enable universe
sudo apt install software-properties-common -y
sudo add-apt-repository universe

# Add ROS source
sudo apt update -y && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update -y
sudo apt upgrade -y

# Install ROS
sudo apt install ros-jazzy-ros-base ros-jazzy-rmw-cyclonedds-cpp ros-jazzy-teleop-twist-keyboard \
    python3-pip python3-colcon-common-extensions rpi.gpio-common -y

# Configure ROS environment
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=1" >> ~/.bashrc
echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
source ~/.bashrc

# Dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh # Install uv
source $HOME/.local/bin/env
sudo usermod -aG dialout ubuntu # GPIO setup

# Install project
git clone https://github.com/Other-Project/SI5-PER.git ~/project --recursive
