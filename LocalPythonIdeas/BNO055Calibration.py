import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import os
import hid
import socket
import json

os.environ["BLINKA_MCP2221"] = "1"
device = hid.device()
device.open(0x04D8, 0x00DD)

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
# Your accelerometer data updating code
# For this example, I'll simulate some dummy data with a function
import math
# Your accelerometer data updating code
# For this example, I'll simulate some dummy data with a function
import math
def get_acceleration_data(t):
    return math.sin(t)


# Lists to store data for plotting
times = []
positions = []
velocities = []
accelerations = []
realaccelerations = []

# Parameters
start_time = time.time()
current_time = time.time()
previous_time = time.time()
total_time = 5  # total time for which we'll collect and plot data

# Initial conditions
velocity = 0
position = 0
calibration = 0

t = 0

while t < total_time:
    AcX,AcY,AcZ = sensor.linear_acceleration
    #AcZ += 0.0232
    # Get current time
    current_time = time.time()
    # Compute deltaTime (in seconds)
    #deltaTime = current_time - previous_time
    deltaTime = 0.01
    accelerations.append(AcZ)
    if t > 1.25:
        print("Start Calibration")
        calibration += 1
        if calibration >= 2:
            if accelerations[calibration-1]-accelerations[calibration-2] > 1.5 or accelerations[calibration-1]-accelerations[calibration-2] < -1.5  :
                # Create the variables
                velocity += AcZ * deltaTime
                position += velocity * deltaTime
                # store data
                times.append(t)
                realaccelerations.append(AcZ)
                velocities.append(velocity)
                positions.append(position)
                # Get current time
                current_time = time.time()
        else:
            realaccelerations.append(0)
            velocities.append(0)
            positions.append(0)
            times.append(0)
    # Update previous time
    t += deltaTime
    previous_time = current_time

# Plot
print(len(times))
print(len(realaccelerations))
print(accelerations)
plt.subplot(3, 1, 1)
plt.title('Acceleration vs Time')
plt.plot(times, realaccelerations)
plt.ylabel('Acceleration')

plt.subplot(3, 1, 2)
plt.title('Velocity vs Time')
plt.plot(times, velocities)
plt.ylabel('Velocity')

plt.subplot(3, 1, 3)
plt.title('Position vs Time')
plt.plot(times, positions)
plt.ylabel('Position')

plt.tight_layout()
plt.show()