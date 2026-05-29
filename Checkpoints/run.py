import serial

for baud in [115200, 230400, 256000]:
    print(f"Testing {baud}...")
    ser = serial.Serial('COM18', baud, timeout=1)
    print(ser.read(50))
    ser.close()