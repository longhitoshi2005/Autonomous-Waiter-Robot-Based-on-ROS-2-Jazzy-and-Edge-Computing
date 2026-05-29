#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import json

class WaiterBridgeNode(Node):

    def __init__(self):
        super().__init__('waiter_bridge_node')
        
        # 🟢 1. CẤU HÌNH THÔNG SỐ MQTT KHỚP VỚI ID 210905 CỦA EM
        self.MQTT_SERVER = "mqtt.ohstem.vn"
        self.MQTT_PORT = 1883
        self.MQTT_SUB_TOPIC = "210905/feeds/V1"  # Kênh UP 4000 lắng nghe Encoder + Yaw từ xe
        self.MQTT_PUB_TOPIC = "210905/feeds/V3"  # Kênh UP 4000 bắn lệnh JSON xuống xe
        
        # Khởi tạo Client MQTT
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        self.get_logger().info("Đang kết nối tới Server MQTT OhStem...")
        self.mqtt_client.connect(self.MQTT_SERVER, self.MQTT_PORT, 60)
        
        # Chạy luồng ngầm MQTT để không làm treo ROS 2
        self.mqtt_client.loop_start()

        # 🤖 2. CẤU HÌNH ROS 2 FOXY
        # Subscriber: Hứng vận tốc điều khiển từ bàn phím / Nav2 điều hướng
        self.velocity_subscriber = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10 # Quality of Service (QoS) chuẩn Foxy
        )
        
        # Publisher: Phát dữ liệu cảm biến nhận từ xe lên hệ thống ROS 2
        self.telemetry_publisher = self.create_publisher(String, '/vehicle/telemetry', 10)
        
        self.get_logger().info("Node cầu nối ROS 2 Foxy đã SẴN SÀNG!")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.get_logger().info("Đã thông mạng MQTT! Đang đăng ký nghe kênh V1...")
            self.mqtt_client.subscribe(self.MQTT_SUB_TOPIC)
        else:
            self.get_logger().error(f"Kết nối MQTT thất bại với mã lỗi: {rc}")

    # 🚀 CHIỀU LÊN: Nhận dữ liệu Encoder + Yaw từ xe gửi lên, đẩy vào hệ thống ROS 2
    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            
            # Khởi tạo Message dạng String của ROS 2 để phát đi
            ros_msg = String()
            ros_msg.data = payload
            self.telemetry_publisher.publish(ros_msg)
            
            # In Log ra màn hình để em dễ giám sát trạng thái xe
            self.get_logger().info(f"-> Xe phản hồi: {payload}")
        except Exception as e:
            self.get_logger().error(f"Lỗi xử lý dữ liệu chiều lên: {e}")

    # ⚡ CHIỀU XUỐNG: Hứng từ lệnh di chuyển của ROS 2, đóng gói JSON bắn xuống xe
    def cmd_vel_callback(self, msg: Twist):
        try:
            # Trích xuất vận tốc tuyến tính x, y và vận tốc góc z từ góc nhìn của ROS 2
            vx = msg.linear.x
            vy = msg.linear.y
            wz = msg.angular.z
            
            # Đóng gói chuẩn xác thành cấu trúc Dictionary Python
            command_dict = {
                "vx": round(vx, 2),
                "vy": round(vy, 2),
                "wz": round(wz, 2)
            }
            
            # Biến đổi sang chuỗi JSON sạch kèm ký tự ngắt dòng \n
            json_payload = json.dumps(command_dict) + "\n"
            
            # Bắn thô (raw) xuống thẳng kênh V3 của con xe YOLO Uno
            self.mqtt_client.publish(self.MQTT_PUB_TOPIC, json_payload)
            
        except Exception as e:
            self.get_logger().error(f"Lỗi đóng gói lệnh JSON gửi xuống xe: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = WaiterBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Đang tắt Node cầu nối...")
    finally:
        node.mqtt_client.loop_stop()
        node.mqtt_client.disconnect()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()