# First try to get the velocity from visual odometry
# If can't get confident estimate resort to getting velocity from BNO055
# Return whatever you decide to go with

"""
This is the code required to retrieve the basic BNO055 linear acceleration and then integrate with time to get the velocity (Very Error Heavy )
"""

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
sensor = adafruit_bno055.BNO055_I2C(i2c)

last_val = 0xFFFF

"""
This is the code on how to retrieve velocity information from visual odometry 
"""
