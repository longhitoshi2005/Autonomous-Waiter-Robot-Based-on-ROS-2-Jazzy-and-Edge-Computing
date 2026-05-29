import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Get the package share directory
    pkg_share = get_package_share_directory('waiter_description')
    xacro_file = os.path.join(pkg_share, 'urdf', 'roboco.urdf.xacro')
    
    # Process URDF
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # Robot State Publisher for RViz
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_raw,
            'use_sim_time': True
        }]
    )

    # Include the Nav2 RViz launch
    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'rviz_launch.py')]),
        launch_arguments={
            'use_sim_time': 'True'
        }.items(),
    )

    return LaunchDescription([
        rviz_launch
    ])