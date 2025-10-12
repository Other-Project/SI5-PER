#!/bin/bash

# -----------------------------
#
# These instructions are for Ubuntu 24.04
#
# -----------------------------


# Enable universe
sudo apt install software-properties-common
sudo add-apt-repository universe

# Add ROS source
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt upgrade

# Install ROS
sudo apt install ros-jazzy-desktop

# Add Gazebo source
sudo apt-get install lsb-release gnupg
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-prerelease $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-prerelease.list > /dev/null
sudo apt-get update

# Install Gazebo
sudo apt-get install gz-harmonic

# Install ROS Crazyflies
sudo apt install libboost-program-options-dev libusb-1.0-0-dev python3-colcon-common-extensions
sudo apt install ros-jazzy-motion-capture-tracking ros-jazzy-tf-transformations ros-jazzy-teleop-twist-keyboard
sudo apt install ros-jazzy-ros-gz

# Install Python dependancies
sudo apt install python3-transforms3d
pip3 install --break-system-packages cflib

