import numpy as np
import cv2
import pyrealsense2 as rs
import math

def distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Initialize ORB detector
orb = cv2.ORB_create()

# Brute-force Matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Previous frame data
prev_gray = None
prev_kps = None
prev_descs = None

try:
    while True:
        # Get frameset of depth and color
        frames = pipeline.wait_for_frames()
        current_depth_frame = frames.get_depth_frame()
        current_depth_image = np.asanyarray(current_depth_frame.get_data())
        current_depth_image = cv2.flip(current_depth_image, -1)
        depth_intrinsics = frames.profile.as_video_stream_profile().intrinsics

        color_frame = frames.get_color_frame()

        # Convert color frame to numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Convert to grayscale for ORB
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Detect ORB keypoints and descriptors
        kps, descs = orb.detectAndCompute(gray, None)

        # Getting the averages of all the points
        avgDist = 0
        index = 0
        # Match with previous frame's keypoints and descriptors, if available
        if prev_gray is not None:
            matches = bf.match(prev_descs, descs)
            for match in matches:
                # Increase the index
                index += 1
                # Previous frame's coordinate
                prev_pt = prev_kps[match.queryIdx].pt
                # Current frame's coordinate
                curr_pt = kps[match.trainIdx].pt
                # Get the depths of the frames
                prev_depth = prev_depth_image[int(prev_pt[1])][int(prev_pt[0])]
                current_depth = current_depth_image[int(curr_pt[1])][int(curr_pt[0])]
                # Get the actual coordinate point of the point
                prevCoord = rs.rs2_deproject_pixel_to_point(depth_intrinsics, prev_pt, prev_depth)
                currCoord = rs.rs2_deproject_pixel_to_point(depth_intrinsics, curr_pt, current_depth)
                # Grab the distance
                avgDist += distance(prevCoord,currCoord)
            print("Distance Traveled Between Frames:",(avgDist/index))
        # Update the previous frame data
        prev_gray = gray
        prev_kps = kps
        prev_descs = descs
        prev_depth_image = current_depth_image

except KeyboardInterrupt:
    pass

finally:
    pipeline.stop()