import numpy as np
import cv2
import pyrealsense2 as rs

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
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
TOP_PERCENTAGE = 0.1  # Top 10% best matches

try:
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

        # Normalize the depth image for visualization
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Convert to grayscale for ORB
        gray = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2GRAY)

        # Detect ORB keypoints and descriptors
        kps, descs = orb.detectAndCompute(gray, None)

        # Match with previous frame's keypoints and descriptors, if available
        if prev_gray is not None:
            matches = bf.match(prev_descs, descs)

            if len(matches) > 0:
                # Sort the matches based on distance
                matches = sorted(matches, key=lambda x: x.distance)

                # Percentage-based Filtering
                num_good_matches = int(len(matches) * TOP_PERCENTAGE)
                good_matches_percentage = matches[:num_good_matches]

                if len(good_matches_percentage) > 0:
                    matched_image = cv2.drawMatches(prev_gray, prev_kps, gray, kps, good_matches_percentage, None)
                    cv2.imshow('ORB Matches', matched_image)
                else:
                    cv2.imshow('Depth Map', depth_colormap)

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
