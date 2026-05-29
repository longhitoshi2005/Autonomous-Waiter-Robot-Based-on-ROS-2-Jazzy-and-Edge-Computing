# Autonomous Waiter Robot Based on ROS 2 Jazzy and Edge Computing

This project contains the simulation, navigation setup, documentation, and hardware-side code for an autonomous waiter robot. The ROS 2 workspace focuses on a waiter robot model that can run in Gazebo, publish robot state, use lidar/IMU/odometry bridges, and launch Nav2 for map-based navigation.

## Project Structure

- `ros2_ws/` - ROS 2 Jazzy workspace.
- `ros2_ws/src/waiter_description/` - Main robot package with URDF/Xacro model, Gazebo world, maps, Nav2 config, and launch files.
- `ros2_ws/src/sllidar_ros2/` - SLLIDAR ROS 2 driver source.
- `DOAN/` - MicroPython/embedded controller code.
- `Checkpoints/` - Development notes, checkpoint documents, and test scripts.
- `3Dmodel/` - STL/SCAD mechanical model files.
- `Report/` - Final report, LaTeX source, diagrams, and result images.

## Main Features

- ROS 2 Jazzy robot description package.
- Gazebo simulation world: `room_20m2.sdf`.
- Robot model: `roboco.urdf.xacro`.
- Nav2 configuration and saved map for autonomous navigation.
- RViz launch support for navigation visualization.
- SLAM Toolbox launch configuration.
- SLLIDAR integration for laser scan data.

## Quick Start

Open a terminal in `ros2_ws`:

```bash
colcon build --symlink-install
source install/setup.bash
ros2 launch waiter_description gazebo.launch.py
```

In another terminal, launch Nav2:

```bash
source install/setup.bash
ros2 launch waiter_description navigation.launch.py
```

In another terminal, open RViz:

```bash
source install/setup.bash
ros2 launch waiter_description rviz_nav.launch.py
```

## Notes

- Generated folders such as `build/`, `install/`, and `log/` are ignored by Git.
- The main ROS package is `waiter_description`.
- The saved map is located at `ros2_ws/src/waiter_description/maps/my_room_map.yaml`.
