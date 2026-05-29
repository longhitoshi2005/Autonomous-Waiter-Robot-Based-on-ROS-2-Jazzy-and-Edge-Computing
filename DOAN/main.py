import sys
import ujson
import uselect
import time
import uasyncio
from motor import *
from mdv2 import *
from drivebase import *
from mpu6050 import MPU6050
from angle_sensor import AngleSensor

md_v2 = MotorDriverV2()
motor1 = DCMotor(md_v2, E2, reversed=False)
motor2 = DCMotor(md_v2, E1, reversed=False)
motor3 = DCMotor(md_v2, M1, reversed=False)
motor4 = DCMotor(md_v2, M2, reversed=False)

robot = DriveBase(MODE_MECANUM, m1=motor1, m2=motor2, m3=motor3, m4=motor4)

imu = MPU6050()
angle_sensor = AngleSensor(imu)

ROS2_MODE = False
last_ros2_time = 0

async def task_ros2_receiver():
    global ROS2_MODE, last_ros2_time
    spoll = uselect.poll()
    spoll.register(sys.stdin, uselect.POLLIN)
    while True:
        if spoll.poll(0):
            line = sys.stdin.readline().strip()
            if line and line.startswith("{"):
                try:
                    data = ujson.loads(line)
                    vx = data.get("vx", 0.0)
                    vy = data.get("vy", 0.0)
                    wz = data.get("wz", 0.0)
                    ROS2_MODE = True
                    last_ros2_time = time.ticks_ms()
                    speed_x = int(vx * 100)
                    speed_y = int(vy * 100)
                    speed_w = int(wz * 100)
                    robot.move(speed_x, speed_y, speed_w)
                except:
                    pass
        if ROS2_MODE:
            if time.ticks_diff(time.ticks_ms(), last_ros2_time) > 1000:
                robot.stop()
                ROS2_MODE = False
        await uasyncio.sleep_ms(15)

async def task_ros2_telemetry():
    while True:
        try:
            enc1_val = motor1.get_encoder()
            enc2_val = motor2.get_encoder()
            gyro_yaw = angle_sensor.get_angle()
            telemetry = {
                "e1": int(enc1_val),
                "e2": int(enc2_val),
                "yaw": float(gyro_yaw)
            }
            print(ujson.dumps(telemetry))
        except:
            pass
        await uasyncio.sleep_ms(20)

async def main():
    motor1.set_encoder(rpm=350, ppr=11, gears=48)
    motor2.set_encoder(rpm=350, ppr=11, gears=48)
    robot.size(wheel=80, width=485)
    robot.use_gyro(False)
    angle_sensor.calibrate(210)
    uasyncio.create_task(angle_sensor.run())
    robot.angle_sensor(angle_sensor)
    robot.speed(80, min_speed=40)
    uasyncio.create_task(task_ros2_receiver())
    uasyncio.create_task(task_ros2_telemetry())
    while True:
        await uasyncio.sleep_ms(100)

run_loop(main())