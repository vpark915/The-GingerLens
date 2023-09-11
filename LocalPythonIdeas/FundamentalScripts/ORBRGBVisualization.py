import numpy as np
import cv2
import pyrealsense2 as rs

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)

# Initialize ORB detector
orb = cv2.ORB_create()

# Brute-force Matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Previous frame data
prev_gray = None
prev_kps = None
prev_descs = None

MAX_MATCH_DISTANCE = 40  # You can change this threshold based on your needs

try:
    while True:
        # Get frameset of depth and color
        frames = pipeline.wait_for_frames()
        current_depth_frame = frames.get_depth_frame()
        current_depth_image = np.asanyarray(current_depth_frame.get_data())

        color_frame = frames.get_color_frame()

        # Convert color frame to numpy array
        color_image = np.asanyarray(color_frame.get_data())

        # Convert to grayscale for ORB
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Detect ORB keypoints and descriptors
        kps, descs = orb.detectAndCompute(gray, None)

        # Match with previous frame's keypoints and descriptors, if available
        if prev_gray is not None:
            matches = bf.match(prev_descs, descs)

            if len(matches) > 0:
                # Sort the matches based on distance (lowest distance is better)
                matches = sorted(matches, key=lambda x: x.distance)

                # Filter matches based on a distance threshold
                good_matches = [m for m in matches if m.distance < MAX_MATCH_DISTANCE]

                if len(good_matches) > 0:
                    matched_image = cv2.drawMatches(prev_gray, prev_kps, gray, kps, good_matches, None)
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