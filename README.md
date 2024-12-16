# px4-simulation-gazebo
Construction Site Safety using a Drone with PX4 Autopilot and ROS 2. PX4 SITL and Gazebo Garden used for Simulation.
```

### Installation

### Create a virtual environment
```commandline
# create
python3 -m venv ~/px4-venv

# activate
source ~/px4-venv/bin/activate
```
### Clone repository
```commandline
git clone https://github.com/anhducad1111/px4-simulation-gazebo
```
### Install PX4
```commandline
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh
cd PX4-Autopilot/
make px4_sitl
```
### Install ROS 2
```commandline
cd ~
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update && sudo apt upgrade -y
sudo apt install ros-humble-desktop
sudo apt install ros-dev-tools
source /opt/ros/humble/setup.bash && echo "source /opt/ros/humble/setup.bash" >> .bashrc
pip install -U empy pyros-genmsg setuptools
```
### Setup Micro XRCE-DDS Agent & Client
```commandline
cd ~
git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig /usr/local/lib/
```
### Install pip package
```commandline
source ~/px4-venv/bin/activate
pip install mavsdk empy==3.3.4 'numpy<2' lark catkin_pkg
pip install aioconsole
pip install pygame
sudo apt install ros-humble-ros-gzgarden
pip install numpy
pip install opencv-python
pip install ultralytics
```

### Build ROS 2 Workspace
```commandline
mkdir -p ~/ws_sensor_combined/src/
cd ~/ws_sensor_combined/src/
git clone https://github.com/PX4/px4_msgs.git
git clone https://github.com/PX4/px4_ros_com.git
cd ..
source /opt/ros/humble/setup.bash
colcon build

mkdir -p ~/ws_offboard_control/src/
cd ~/ws_offboard_control/src/
git clone https://github.com/PX4/px4_msgs.git
git clone https://github.com/PX4/px4_ros_com.git
cd ..
source /opt/ros/humble/setup.bash
colcon build
```

### Additional Configs
- Put below lines in your bashrc:
```commandline
# Source ROS 2 Humble setup
source /opt/ros/humble/setup.bash

# Export GZ_SIM_RESOURCE_PATH
export GZ_SIM_RESOURCE_PATH=~/.gz/models

# Copy models to ~/.gz/models
mkdir -p ~/.gz/models
cp -r /px4-simulation-gazebo/models/* ~/.gz/models/

# Copy default.sdf to the appropriate directory
mkdir -p ~/PX4-Autopilot/Tools/simulation/gz/worlds/
cp /px4-simulation-gazebo/worlds/default.sdf ~/PX4-Autopilot/Tools/simulation/gz/worlds/

# Change the angle of Drone's camera
sed -i '9s/<pose>.12 .03 .242 0 0 0<\/pose>/<pose>.15 .029 .21 0 0.7854 0<\/pose>/' ~/PX4-Autopilot/Tools/simulation/gz/models/x500_depth/model.sdf

echo "Setup completed successfully."
```

## Run
You need several terminals.
```commandline
Terminal #1:
cd ~/Micro-XRCE-DDS-Agent
MicroXRCEAgent udp4 -p 8888

Terminal #2:
source ~/.bashrc
cd ~/PX4-Autopilot
make clean
source ~/px4-venv/bin/activate
PX4_GZ_MODEL_POSE="-30,-30,4,0,0,0.9"  make px4_sitl gz_x500_depth

Terminal #3:
ros2 run ros_gz_image image_bridge /camera

Terminal #4:
source ~/px4-venv/bin/activate
cd ~/px4-simulation-gazebo
python uav_camera_det.py
```
### Fly using Keyboard
```commandline
Terminal #5:
source ~/px4-venv/bin/activate
cd ~/px4-simulation-gazebo
python keyboard-mavsdk-test.py
```
When you run the last command a blank window will open for reading inputs from keyboard. focus on that window by clicking on it, then hit "r" on keyboard to arm the drone, and use WASD and Up-Down-Left-Right on the keyboard for flying, and use "l" for landing.

### Fly using ROS 2
```commandline
Terminal #5:
cd ~/ws_offboard_control
source /opt/ros/humble/setup.bash
source install/local_setup.bash
ros2 run px4_ros_com offboard_control
```
### Fly automation
```commandline
Terminal #5:
source ~/px4-venv/bin/activate
cd ~/px4-simulation-gazebo
python ps.py
```

## Acknowledgement
- https://github.com/PX4/PX4-Autopilot
- https://github.com/ultralytics/ultralytics
- https://www.ros.org/
- https://gazebosim.org/

