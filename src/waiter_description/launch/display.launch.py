import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Tìm đường dẫn file config
    slam_params_path = os.path.join(
        get_package_share_directory('waiter_description'),
        'config',
        'mapper_params_online_async.yaml'
    )

    # 2. Khai báo Node SLAM Toolbox
    start_async_slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_path,
            {'use_sim_time': True} # Bắt buộc phải True khi chạy Gazebo [cite: 1]
        ]
    )

    return LaunchDescription([
        start_async_slam_toolbox_node
    ])