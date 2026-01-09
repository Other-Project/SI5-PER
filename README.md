# Autonomous Drone Landing on a Moving Platform

<p align=center>
    <img src=".assets/ab2-platform.png" width="20%" alt="Alphabot 2" />
    <img src=".assets/crazyflie.png" width="20%" alt="Crazyflie 2.1+" /><br/>
    <a href="https://releases.ubuntu.com/noble/">
        <img alt="Ubuntu 24.04" src="https://img.shields.io/badge/-UBUNTU%2024%2E04-orange?style=flat-square&logo=ubuntu&logoColor=white" />
    </a>
    <a href="https://docs.ros.org/en/jazzy/index.html">
        <img alt="ROS Jazzy" src="https://img.shields.io/badge/-ROS%20JAZZY-blue?style=flat-square&logo=ros" />
    </a><br />
    <span>Work carried out by <a href="https://github.com/komi-assimpah">Komi Jean-Paul Assimpah</a>, <a href="https://github.com/AlbanFALCOZ">Alban Falcoz</a>, <a href="https://github.com/06Games">Evan Galli</a> and <a href="https://github.com/Alexandre-Gripari">Gripari Alexandre</a>
    <br/>as part of the <b>Study and Research Project</b>.</span>
</p>

This project aims to implement a collaborative system allowing a Crazyflie 2.1+ nano-drone to autonomously land on a moving Waveshare AlphaBot2 platform.

Developed under ROS 2 Jazzy, the system uses Deep Reinforcement Learning to coordinate the drone's trajectory based on real-time sensor fusion (Flow Deck v2 and camera tracking).

The guidance strategy is first trained in NVIDIA IsaacSim (coupled with IsaacLab). 
The models are subsequently validated in Gazebo to study the transferability between different simulation engines (Sim2Sim). 

The system can then be deployed on physical hardware to analyze and bridge the reality gap (Sim2Real).

## Installation

1. Clone this repository using :  
    ```
    git clone https://github.com/Other-Project/SI5-PER.git --recursive
    ```

2. Install ROS (Jazzy) and Gazebo (Harmonic).  
    An helper script is available for Ubuntu: `utils/install.sh`

3. [Install uv](https://docs.astral.sh/uv/#installation) for managing Python dependencies

## Usage

* `make ros`: Builds ROS packages
* `make sim`: Starts the Gazebo simulation
* `make teleop`: Manually control the drone
* `make clean`: Removes the build artifacts
* `make isaac`: Starts a train or evaluation session in Isaac Sim
