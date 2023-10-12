import numpy as np
import cv2
import pyrealsense2 as rs
import math

"""INTIALIZING REALSENSE DATA"""
# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Initialize ORB detector
orb = cv2.ORB_create()

# Brute-force Matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Previous frame data
prev_gray = None
prev_kps = None
prev_descs = None
prev_matched_coords = None
current_matched_coords = None
MAX_MATCH_DISTANCE = 40  # You can change this threshold based on your needs
TOP_PERCENTAGE = 0.1  # Top 10% best matches

# LIST OF DISTANCE VECTORS
real_points = None
distance_vectors = None
euler_prediction = None


def rotation_matrix(theta_x, theta_y, theta_z):
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(theta_x), -np.sin(theta_x)],
                   [0, np.sin(theta_x), np.cos(theta_x)]])

    Ry = np.array([[np.cos(theta_y), 0, -np.sin(theta_y)],  # Note the negative sign for sin(theta_y)
                   [0, 1, 0],
                   [np.sin(theta_y), 0, np.cos(theta_y)]])

    Rz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                   [np.sin(theta_z), np.cos(theta_z), 0],
                   [0, 0, 1]])

    R = np.dot(Rz, np.dot(Ry, Rx))
    return R


def euler_displacement(theta_x, theta_y, theta_z, point):
    return np.dot(rotation_matrix(theta_x, theta_y, theta_z), point)


def distance_point(point):
    distance = math.sqrt(point[0] ** 2 + point[1] ** 2 + point[2] ** 2)
    return distance


def average_vectors(vectors):
    if not vectors:
        return None  # return None if the list is empty

    total_x = sum(vec[0] for vec in vectors)
    total_y = sum(vec[1] for vec in vectors)
    total_z = sum(vec[2] for vec in vectors)

    num_vectors = len(vectors)

    return [total_x / num_vectors, total_y / num_vectors, total_z / num_vectors]


def average_list(list):
    return sum(list) / len(list)


def vector_between_points(p1, p2):
    return [p2[i] - p1[i] for i in range(3)]


"""INTIATING BNO055 ROTATIONAL DATA"""
import os
import hid

os.environ["BLINKA_MCP2221"] = "1"
device = hid.device()
device.open(0x04D8, 0x00DD)

import board
import adafruit_bno055

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_bno055.BNO055_I2C(i2c)
last_val = 0xFFFF

"""MAIN LOOP"""
try:
    while True:
        """RGB AND DEPTH DATA PROCESSING"""
        # Create alignment
        align_to = rs.stream.color
        align = rs.align(align_to)
        # Get frameset of depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        depth_intrinsics = frames.profile.as_video_stream_profile().intrinsics
        color_frame = frames.get_color_frame()

        # Convert color frame to numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Convert to grayscale for ORB
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Detect ORB keypoints and descriptors
        kps, descs = orb.detectAndCompute(gray, None)

        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        depth_with_kps = cv2.drawKeypoints(depth_colormap, kps, None, color=(0, 255, 0), flags=0)
        cv2.imshow('Depth with Keypoints', depth_with_kps)

        # Match with previous frame's keypoints and descriptors, if available
        if prev_gray is not None:
            matches = bf.match(prev_descs, descs)

            if len(matches) > 0:
                # Sort the matches based on distance (lowest distance is better)
                matches = sorted(matches, key=lambda x: x.distance)

                # Filter matches based on a distance threshold
                good_matches = [m for m in matches if m.distance < MAX_MATCH_DISTANCE]

                """PERCENTAGE BASED FILTERING"""
                # 1. Percentage-based Filtering
                num_good_matches = int(len(matches) * TOP_PERCENTAGE)
                good_matches_percentage = matches[:num_good_matches]

                # Extract (x, y) coordinates of matched keypoints
                prev_matched_coords = [prev_kps[match.queryIdx].pt for match in good_matches_percentage]
                current_matched_coords = [kps[match.trainIdx].pt for match in good_matches_percentage]

                # Print matched coordinates (You can store or process them further based on your needs)
                print("Previous Frame Matched Coordinates:", prev_matched_coords)
                print("Current Frame Matched Coordinates:", current_matched_coords)
                print("Depth of current:",
                      depth_image[int(current_matched_coords[0][1])][int(current_matched_coords[0][0])])

                if len(good_matches) > 0:
                    matched_image = cv2.drawMatches(prev_gray, prev_kps, gray, kps, good_matches_percentage,
                                                    None)  # or replace 'good_matches_percentage' with 'good_matches_ratio'
                    cv2.imshow('Filtered Matched keypoints', matched_image)

        # Update the previous frame data
        prev_gray = gray
        prev_kps = kps
        prev_descs = descs

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

finally:
    pipeline.stop()
    cv2.destroyAllWindows()