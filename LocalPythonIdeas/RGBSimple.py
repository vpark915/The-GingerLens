import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize ORB detector
orb = cv2.ORB_create()

# Initialize BFMatcher (Brute Force Matcher)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# Read the first frame
ret, old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

# Compute ORB keypoints and descriptors for the first frame
kp1, des1 = orb.detectAndCompute(old_gray, None)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Compute ORB keypoints and descriptors for the new frame
    kp2, des2 = orb.detectAndCompute(frame_gray, None)

    # Match descriptors between the old frame and the new frame
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Draw the matches
    out_frame = cv2.drawMatches(old_frame, kp1, frame, kp2, matches[:10], None,
                                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    cv2.imshow('ORB Tracking', out_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Update the old frame and its keypoints
    old_frame = frame.copy()
    kp1, des1 = kp2, des2

cap.release()
cv2.destroyAllWindows()