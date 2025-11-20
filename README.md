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
