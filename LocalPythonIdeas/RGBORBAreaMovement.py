import cv2
import numpy as np
import pyrealsense2 as rs

# Initialize and configure the RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Set up the configuration for infrared stream
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)

# Start the pipeline
pipeline.start(config)

# Initialize feature detector with fewer features and matcher
detector = cv2.ORB_create(nfeatures=300)  # Only retain 300 features
bf = cv2.BFMatcher(cv2.NORM_HAMMING)

prev_kp = None
prev_des = None
prev_image = None

while True:
    # Get frameset of infrared
    frames = pipeline.wait_for_frames()
    ir_frame = frames.get_infrared_frame(1)
    ir_image = np.asanyarray(ir_frame.get_data())

    # Detect ORB keypoints and descriptors
    kp, des = detector.detectAndCompute(ir_image, None)

    if prev_kp is not None and prev_des is not None and des is not None:
        matches = bf.knnMatch(prev_des, des, k=2)

        # Filter matches using Lowe's ratio test
        good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

        # Draw only the top 50 matches (or fewer if there aren't that many)
        im_matches = cv2.drawMatches(prev_image, prev_kp, ir_image, kp, good_matches[:50], None)
        cv2.imshow("Matches", im_matches)

    # Store current keypoints and descriptors for the next iteration
    prev_kp = kp
    prev_des = des
    prev_image = ir_image.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

pipeline.stop()
cv2.destroyAllWindows()
