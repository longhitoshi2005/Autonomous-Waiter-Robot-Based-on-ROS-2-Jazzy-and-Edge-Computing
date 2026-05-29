Terminal 1
colcon build --symlink-install
source install/setup.bash
ros2 launch waiter_description gazebo.launch.py

Terminal 2
ros2 launch nav2_bringup bringup_launch.py use_sim_time:=True map:=/mnt/c/BKHCM/Year_3/HK252/DADN/ros2_ws/src/waiter_description/maps/my_room_map.yaml

Terminal 3
ros2 launch waiter_description rviz_nav.launch.py