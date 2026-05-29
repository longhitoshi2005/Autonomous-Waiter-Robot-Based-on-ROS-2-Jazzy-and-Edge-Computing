1. Quản lý Không gian làm việc (Workspace)Lệnh khởi tạo và xây dựng hệ thống sau khi chỉnh sửa code.Bash# Di chuyển vào thư mục gốc của workspace
cd ~/ros2_ws

# Xóa bỏ các bản build cũ để làm sạch hệ thống (khi gặp lỗi cấu trúc)
rm -rf build/ install/ log/

# Biên dịch riêng package waiter_description
colcon build --packages-select waiter_description

# Cập nhật cấu hình môi trường (Bắt buộc chạy mỗi khi mở terminal mới)
source install/setup.bash

2. Quy trình Khởi chạy Mô phỏng (4 Bước)Bước 1: Mở Gazebo Sim (Môi trường vật lý)Bash
ros2 launch waiter_description gazebo.launch.py
Lưu ý: Luôn nhấn nút Play ở góc dưới bên trái Gazebo.

Bước 2: Khởi động Bridge (Cầu nối ROS 2 <-> Gazebo)Đây là lệnh tổng hợp để thông toàn bộ các luồng dữ liệu quan trọng:

Bash
ros2 run ros_gz_bridge parameter_bridge \
/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist \
/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan \
/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V \
/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry \
/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model

Bước 3: Giám sát bằng RViz2 (Môi trường hiển thị)Bashrviz2
Cấu hình trong RViz:Fixed Frame: Đổi thành base_link hoặc odom.Add -> RobotModel: Chọn Description Topic là /robot_description. Add -> LaserScan: Chọn Topic là /scan, chỉnh Size lên 0.05.

Bước 4: Điều khiển bằng bàn phím
Bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard


3. Các lệnh Kiểm tra & Gỡ lỗi (Debugging)Dùng khi robot không hiện hoặc không di chuyển.
Lệnh                            Mục đích
ros2 pkg list | grep waiter     Kiểm tra hệ thống đã nhận package chưa

ros2 topic list                 Xem danh sách các topic đang hoạt động

ros2 topic echo /scan           Kiểm tra dữ liệu Lidar có đang đổ về không

ros2 run tf2_tools view_frames  Kiểm tra cấu trúc cây tọa độ (TF Tree)


4. Danh sách các File Quan trọngroboco.urdf.xacro: Định nghĩa phần cứng, khối lượng và các Plugin (Mecanum Drive, Lidar, Joint State).gazebo.launch.py: Tự động gọi Gazebo Sim và thả robot vào tọa độ mong muốn.package.xml: Chứa thông tin về dependencies (phụ thuộc) của package.

5. Lưu ý đặc biệt cho Jazzy/Gazebo SimPlugin Name: Luôn sử dụng tiền tố gz-sim- (ví dụ: gz-sim-mecanum-drive-system).Bridge Syntax: Dấu [ nghĩa là dữ liệu từ Gazebo sang ROS, dấu ] là từ ROS sang Gazebo, và @ là dữ liệu đi được cả hai chiều.