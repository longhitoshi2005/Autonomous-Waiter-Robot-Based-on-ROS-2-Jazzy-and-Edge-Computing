import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_share = get_package_share_directory('waiter_description')
    nav2_params_path = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    # Dùng đường dẫn tuyệt đối (trực tiếp vào thư mục src) để không bị lỗi thiếu file
    map_path = '/mnt/c/BKHCM/Year_3/HK252/DADN/ros2_ws/src/waiter_description/maps/my_room_map.yaml'

    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py')]),
        launch_arguments={
            'use_sim_time': 'True',
            'autostart': 'True',
            'params_file': nav2_params_path,
            'map': map_path,
            'use_collision_monitor': 'False'
        }.items(),
    )

    return LaunchDescription([nav2_bringup_launch])