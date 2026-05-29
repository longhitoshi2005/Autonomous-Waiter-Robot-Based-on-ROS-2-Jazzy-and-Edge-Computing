import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Khai báo các đường dẫn thư mục
    pkg_share = get_package_share_directory('waiter_description')
    xacro_file = os.path.join(pkg_share, 'urdf', 'roboco.urdf.xacro')
    world_path = os.path.join(pkg_share, 'worlds', 'room_20m2.sdf')
    
    # 2. Xử lý file URDF/XACRO
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # 3. Node Robot State Publisher (Công bố cấu trúc robot)
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_raw,
            'use_sim_time': True # Bắt buộc True trong mô phỏng
        }]
    )

    # 4. Khởi chạy Gazebo Sim (Môi trường mô phỏng)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={
            'gz_args': f'-r {world_path}' # Sử dụng đường dẫn tuyệt đối đến file world
        }.items(),
    )

    # 5. Node Spawn Robot (Thả robot vào thế giới Gazebo)
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'roboco',
            '-z', '0.1' # Thả robot cách mặt đất 10cm để tránh kẹt sàn
        ],
        output='screen'
    )

    # 6. Node ROS-GZ Bridge (Cầu nối quan trọng nhất)
    # 6. Node ROS-GZ Bridge (Cầu nối quan trọng nhất)
    node_ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',  # Đã sửa thành /odom
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
        ],  
        # Đã xóa remappings vì không còn cần thiết nữa
        output='screen',
        parameters=[{'use_sim_time': True}] 
    )

    # 7. Static transform from odom to world (since Gazebo world is odom frame)
    static_transform_odom_world = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'world'],
        output='screen'
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gazebo,
        spawn_robot,
        node_ros_gz_bridge
    ])