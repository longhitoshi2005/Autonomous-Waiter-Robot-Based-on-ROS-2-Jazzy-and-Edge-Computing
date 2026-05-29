import sys
import ujson
import time
import network
from yolo_uno import *
from motor import *
from mdv2 import *
from mpu6050 import MPU6050         
from angle_sensor import AngleSensor 
from abutton import *
from pins import *
from mqtt_as import MQTTClient, config

# 1. Ép kết nối Wi-Fi bằng thư viện gốc
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

SSID_NAME = 'NgocLong'
WIFI_PASS = '05041978'

wlan.connect(SSID_NAME, WIFI_PASS)
while not wlan.isconnected():
    neopix.show(0, hex_to_rgb('#ff0000'))
    time.sleep_ms(200)
    neopix.show(0, hex_to_rgb('#000000'))
    time.sleep_ms(200)

neopix.show(0, hex_to_rgb('#0000ff'))

# 2. Cấu hình MQTT Broker
cfg = config.copy()
cfg['ssid'] = SSID_NAME
cfg['wifi_pw'] = WIFI_PASS
cfg['server'] = 'mqtt.ohstem.vn'
cfg['port'] = 1883
cfg['user'] = '210905'
cfg['password'] = ''

md_v2 = MotorDriverV2()
imu = MPU6050()
angle_sensor = AngleSensor(imu)
btn_BOOT = aButton(BOOT_PIN)
led_D13 = Pins(D13_PIN)

last_cmd_time = time.ticks_ms()

def deinit():
    md_v2.stop()
    mqtt_client.close()
    btn_BOOT.deinit()

import yolo_uno
yolo_uno.deinit = deinit
mqtt_client = MQTTClient(cfg)

# 🚀 LUỒNG NHẬN LỆNH TỰ HÀNH CHUẨN ROS 2
# 🚀 HÀM NHẬN LỆNH JSON VẠN NĂNG - KHÔNG SỢ RÁC KÝ TỰ ĐẦU CUỐI
async def task_mqtt_receiver():
    global last_cmd_time
    while not mqtt_client._isconnected:
        await asleep_ms(100)
        
    await mqtt_client.subscribe('210905/feeds/V3', 1)
    
    async for topic, msg, retained in mqtt_client.queue:
        try:
            # 🟢 ÉP KIỂU VÀ KHỬ RÁC TUYỆT ĐỐI CHO BYTEARRAY
            if isinstance(msg, (bytes, bytearray)):
                line = msg.decode('utf-8').strip().lower()
            else:
                line = str(msg).strip().lower()
            
            if "{" in line and "}" in line:
                last_cmd_time = time.ticks_ms()
                
                # Cắt lấy chính xác ruột JSON từ dấu { đến }
                start_idx = line.find("{")
                end_idx = line.find("}") + 1
                clean_json = line[start_idx:end_idx]
                
                print("-> CHUỖI JSON SAU KHI LÀM SẠCH VÀ ÉP KIỂU:", clean_json)
                
                # Giải mã JSON sạch - Không bao giờ lo lỗi syntax nữa!
                data = ujson.loads(clean_json)
                vx = float(data.get("vx", 0.0))
                vy = float(data.get("vy", 0.0))
                wz = float(data.get("wz", 0.0))
                
                speed_x = int(vx * 180)
                speed_y = int(vy * 180)
                speed_w = int(wz * 180)
                
                m1_speed = speed_x - speed_y - speed_w
                m2_speed = speed_x + speed_y + speed_w
                m3_speed = speed_x + speed_y - speed_w
                m4_speed = speed_x - speed_y + speed_w
                
                # Giữ nguyên dấu cấu hình chạy thẳng của Linh
                m3_speed = - m3_speed
                m1_speed = - m1_speed
                
                m1_speed = max(min(m1_speed, 100), -100)
                m2_speed = max(min(m2_speed, 100), -100)
                m3_speed = max(min(m3_speed, 100), -100)
                m4_speed = max(min(m4_speed, 100), -100)
                
                md_v2.set_motors(M1, m1_speed)
                md_v2.set_motors(M2, m2_speed)
                md_v2.set_motors(E1, m3_speed)
                md_v2.set_motors(E2, m4_speed)
        except Exception as e:
            print("!!! LỖI TOÁN HỌC:", e)

# Bộ phanh khẩn cấp Watchdog (An toàn tuyệt đối)
async def task_safety_watchdog():
    global last_cmd_time
    while True:
        # Nếu quá 1 giây không có lệnh ROS 2 làm tươi -> Tự động phanh xe
        if time.ticks_diff(time.ticks_ms(), last_cmd_time) > 500:
            md_v2.stop()
        await asleep_ms(50)

async def task_ros2_telemetry():
    try:
        from motor import DCMotor 
        m_enc1 = DCMotor(md_v2, E1) 
        m_enc2 = DCMotor(md_v2, E2) 
        m_enc1.set_encoder(rpm=350, ppr=11, gears=34) 
        m_enc2.set_encoder(rpm=350, ppr=11, gears=34) 
    except:
        pass

    while True:
        try:
            enc1 = m_enc1.encoder_ticks() 
            enc2 = m_enc2.encoder_ticks() 
            yaw_val = angle_sensor.heading 
            payload = '{"e1":' + str(int(enc1)) + ',"e2":' + str(int(enc2)) + ',"yaw":' + str(round(yaw_val, 2)) + '}' 
            await mqtt_client.publish('V1', payload)
        except:
            pass
        await asleep_ms(100)

async def task_blink_led():
    while True:
        await asleep_ms(1000)
        led_D13.toggle()

async def setup():
    print('Connecting MQTT Broker...')
    neopix.show(0, hex_to_rgb('#ffc800'))
    angle_sensor.calibrate(250)
    create_task(angle_sensor.run())
    await mqtt_client.connect()
    neopix.show(0, hex_to_rgb('#00ff00'))
    print('ALL CHANNELS READY!')
    
    create_task(task_blink_led())
    create_task(task_mqtt_receiver())
    create_task(task_safety_watchdog())
    create_task(task_ros2_telemetry())

async def main():
    await setup()
    while True:
        await asleep_ms(100)

run_loop(main())