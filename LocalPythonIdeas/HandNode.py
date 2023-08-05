import numpy as np
import pyrealsense2 as rs
from cvzone.HandTrackingModule import HandDetector
import socket
import cv2

# Create a RealSense camera object and configure it for RGB stream
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30)

# Start streaming
pipeline.start(config)

h, w = 1080, 1920  # Height and width of the RealSense RGB frames
detector = HandDetector(detectionCon=0.8, maxHands=2)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 5052)

while True:
    # Get RealSense RGB frame
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    if not color_frame:
        continue

    # Convert the RealSense RGB frame to a format suitable for OpenCV
    img = np.asanyarray(color_frame.get_data())

    # Find the hand and its landmarks
    hands, img = detector.findHands(img)  # with draw
    # hands = detector.findHands(img, draw=False)  # without draw
    data = []

    if hands:
        # Hand 1
        hand = hands[0]
        lmList = hand["lmList"]  # List of 21 Landmark points
        for lm in lmList:
            data.extend([lm[0], h - lm[1], lm[2]])
        # print(lmList)
        print(data)
        sock.sendto(str.encode(str(data)), serverAddressPort)

pipeline.stop()
cv2.destroyAllWindows()