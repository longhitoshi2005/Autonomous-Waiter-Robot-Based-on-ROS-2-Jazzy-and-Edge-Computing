import sys
import ujson
from motor import *
from mdv2 import *
from drivebase import *
from servo import *
from mpu6050 import MPU6050
from angle_sensor import AngleSensor
from ble import *
from gamepad import *
from yolo_uno import *
from abutton import *
import uselect

# =========================================================================
# KHỞI TẠO PHẦN CỨNG (Giữ nguyên cấu hình xe của em)
# =========================================================================
md_v2 = MotorDriverV2()
motor3 = DCMotor(md_v2, M1, reversed=False)
motor4 = DCMotor(md_v2, M2, reversed=False)
motor1 = DCMotor(md_v2, E2, reversed=False) # Động cơ 1 có encoder
motor2 = DCMotor(md_v2, E1, reversed=False) # Động cơ 2 có encoder
motor5 = DCMotor(md_v2, M4, reversed=False)

# Sử dụng chế độ MECANUM tích hợp sẵn để xử lý cho 4 bánh Omni chữ X
robot = DriveBase(MODE_MECANUM, m1=motor1, m2=motor2, m3=motor3, m4=motor4)

servo1 = Servo(md_v2, S1, 180)
servo2 = Servo(md_v2, S2, 180)
servo3 = Servo(md_v2, S3, 180)
servo4 = Servo(md_v2, S4, 180)
imu = MPU6050()
angle_sensor = AngleSensor(imu)
gamepad = Gamepad()
btn_BOOT = aButton(BOOT_PIN)

# Biến cờ kiểm soát chế độ điều khiển
ROS2_MODE = False
last_ros2_time = 0

# =========================================================================
# SỬA LẠI: TASK 1 - LẮNG NGHE LỆNH VẬN TỐC TỪ ROS2 (KHÔNG GÂY CHẶN LUỒNG)
# =========================================================================
async def task_ros2_receiver():
    global ROS2_MODE, last_ros2_time
    print("ROS2 USB Bridge Task Started. Listening via Type-C (Non-blocking)...")
    
    # Khởi tạo đối tượng kiểm tra luồng đầu vào hệ thống (sys.stdin)
    spoll = uselect.poll()
    spoll.register(sys.stdin, uselect.POLLIN)
    
    while True:
        # Kiểm tra xem cổng USB có dữ liệu mới gửi xuống không (chờ trong 0ms - không chặn)
        if spoll.poll(0):
            # Nếu có dữ liệu, lúc này đọc chắc chắn sẽ không bị treo Task
            line = sys.stdin.readline().strip()
            
            if line and line.startswith("{"):
                try:
                    data = ujson.loads(line)
                    vx = data.get("vx", 0.0)
                    vy = data.get("vy", 0.0)
                    wz = data.get("wz", 0.0)
                    
                    ROS2_MODE = True
                    last_ros2_time = time.ticks_ms()
                    
                    # Quy đổi và áp lệnh điều khiển lên DriveBase của em
                    speed_x = int(vx * 100)
                    speed_y = int(vy * 100)
                    speed_w = int(wz * 100)
                    robot.move(speed_x, speed_y, speed_w)
                    
                except:
                    pass
        
        # Cơ chế Watchdog an toàn: Quá 1 giây không có lệnh ROS2 -> Tự dừng xe
        if ROS2_MODE and time.ticks_diff(time.ticks_ms(), last_ros2_time) > 1000:
            robot.stop()
            ROS2_MODE = False
            neopix.show(0, hex_to_rgb('#ff0000')) # Đèn đỏ báo mất kết nối bộ não
            
        await asleep_ms(15) # Chu kỳ quét mượt mà cho hệ thống bất đồng bộ
        
# =========================================================================
# NEW: TASK 2 - ĐỌC VÀ GỬI PHẢN HỒI ENCODER NGƯỢC LÊN UP 4000 (TẦN SỐ 50Hz)
# =========================================================================
async def task_ros2_telemetry():
    while True:
        # Đọc giá trị số xung (hoặc vận tốc RPM) thực tế từ 2 motor có tích hợp encoder
        # Tùy vào phiên bản thư viện motor của em, hàm có thể là get_encoder_count() hoặc get_speed()
        try:
            enc1_val = motor1.get_encoder() # Đọc giá trị encoder động cơ 1
            enc2_val = motor2.get_encoder() # Đọc giá trị encoder động cơ 2
            gyro_yaw = angle_sensor.get_angle() # Lấy góc quay Yaw từ bộ lọc IMU có sẵn
            
            # Đóng gói dữ liệu thành chuỗi JSON tối giản để tối ưu băng thông cáp USB
            telemetry = {
                "e1": enc1_val,
                "e2": enc2_val,
                "yaw": gyro_yaw
            }
            
            # Bắn thẳng chuỗi lên cổng USB Type-C thông qua lệnh in tiêu chuẩn
            print(ujson.dumps(telemetry))
            
        except:
            pass
            
        await asleep_ms(20) # Phát dữ liệu định kỳ chuẩn tần số 50Hz cho SLAM

# =========================================================================
# CÁC TASK ĐIỀU KHIỂN TAY CẦM PS4 (Giữ nguyên gốc của em)
# =========================================================================
async def task_v_M_x_T():
    global ROS2_MODE
    while True:
        await asleep_ms(75)
        # Chỉ cho phép tay cầm can thiệp khi không ở chế độ tự hành ROS2
        if not ROS2_MODE:
            if gamepad.data[BTN_R1] == 1: await servo1.run_steps(5)
            if gamepad.data[BTN_R2] == 1: await servo1.run_steps(-5)
            if gamepad.data[BTN_UP] == 1: robot.forward()
            if gamepad.data[BTN_DOWN] == 1: robot.backward()
            if gamepad.data[BTN_LEFT] == 1: robot.turn_left()
            if gamepad.data[BTN_RIGHT] == 1: robot.turn_right()
            if (gamepad.data[ALX]) > 40: robot.move_right()
            if (gamepad.data[ALX]) < -40: robot.move_left()
            if (gamepad.data[ALY]) > 40: robot.forward()
            if (gamepad.data[ALY]) < -40: robot.backward()

# =========================================================================
# THIẾT LẬP HỆ THỐNG BAN ĐẦU
# =========================================================================
async def setup():
    print('App started')
    neopix.show(0, hex_to_rgb('#ff0000'))
    
    # Khởi tạo thông số Encoder động cơ (giữ nguyên thông số Gears/PPR của em)
    motor1.set_encoder(rpm=350, ppr=11, gears=48)
    motor2.set_encoder(rpm=350, ppr=11, gears=48)
    robot.size(wheel=80, width=485)
    
    robot.use_gyro(False)
    angle_sensor.calibrate(210)
    create_task(angle_sensor.run())
    robot.angle_sensor(angle_sensor)
    robot.speed(80, min_speed=40)
    neopix.show(0, hex_to_rgb('#0000ff')) # Đèn xanh dương báo hệ thống sẵn sàng

    # Kích hoạt các luồng xử lý bất đồng bộ
    create_task(ble.wait_for_msg())
    create_task(gamepad.run())
    create_task(task_v_M_x_T())
    
    # KÍCH HOẠT 2 TASK TRUYỀN THÔNG MỚI VỚI ROS2
    create_task(task_ros2_receiver())
    create_task(task_ros2_telemetry())

async def main():
    await setup()
    while True:
        await asleep_ms(100)

run_loop(main())