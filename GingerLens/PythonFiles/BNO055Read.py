import os
import hid
import socket
import json

os.environ["BLINKA_MCP2221"] = "1"
device = hid.device()
device.open(0x04D8, 0x00DD)
pid = os.getpid()

with open("PythonFiles/pid.txt", "w") as f:
    f.write(str(pid))

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_bno055

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = adafruit_bno055.BNO055_I2C(i2c)

# If you are going to use UART uncomment these lines
# uart = board.UART()
# sensor = adafruit_bno055.BNO055_UART(uart)

last_val = 0xFFFF


# UDP Sending STUFF
def UDPSend(data):
    # Identify Data String
    data_str = str(data)

    # Identify Ports and IP
    IP = "127.0.0.1"
    PORT = 12345

    # Create a socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the message.
    sock.sendto(data_str.encode(), (IP, PORT))

    sock.close()


def temperature():
    global last_val  # pylint: disable=global-statement
    result = sensor.temperature
    if abs(result - last_val) == 128:
        result = sensor.temperature
        if abs(result - last_val) == 128:
            return 0b00111111 & result
    last_val = result
    return result


def main():
    while True:
        eulerX, eulerY, eulerZ = sensor.euler
        UDPSend([eulerX, eulerY, eulerZ])
        if os.path.exists("PythonFiles/terminate.txt"):
            os.remove("PythonFiles/terminate.txt")
            break
        # FUNCTIONS PREDEFINED
        # print("Temperature: {} degrees C".format(sensor.temperature))
        # print("Accelerometer (m/s^2): {}".format(sensor.acceleration))
        # print("Magnetometer (microteslas): {}".format(sensor.magnetic))
        # print("Gyroscope (rad/sec): {}".format(sensor.gyro))
        # print("Euler angle: {}".format(sensor.euler))
        # print(eulerX)
        # print("Quaternion: {}".format(sensor.quaternion))
        # print("Linear acceleration (m/s^2): {}".format(sensor.linear_acceleration))
        # print("Gravity (m/s^2): {}".format(sensor.gravity))
        # print()
    sock.close()

if __name__ == "__main__":
    main()