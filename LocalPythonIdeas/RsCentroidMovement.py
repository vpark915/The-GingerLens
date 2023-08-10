import numpy as np
from sklearn.linear_model import LinearRegression
import pyrealsense2 as rs
import cv2
import math
import time

def distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
def RetrieveCentroid():
    x_sum = 0
    y_sum = 0
    z_sum = 0
    index = 0
    for row in range(0,480):
        for item in range(0,640):
            depth = depth_image[row][item]
            if (depth > 0 and depth < 10000):
                pixel = [item, row]
                vector = rs.rs2_deproject_pixel_to_point(depth_intrinsics, pixel, depth)
                #Start Summing
                x_sum += vector[0]
                y_sum += vector[1]
                z_sum += vector[2]
                index += 1
    centroidVector3 = [x_sum/index,y_sum/index,z_sum/index]
    return centroidVector3



# Configure the stream and start the pipeline
pipeline = rs.pipeline()
config = rs.config()

# Configure the D415 depth stream
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

pipeline.start(config)

lastCentroid = []
currentCentroid = []

#START LOOP HERE
# Wait for a new set of frames
frames = pipeline.wait_for_frames()

#Retrieve Depth Intrinsics
depth_intrinsics = frames.profile.as_video_stream_profile().intrinsics

# Get the depth frame
depth_frame = frames.get_depth_frame()
depth_image = np.asanyarray(depth_frame.get_data())
depth_image = cv2.flip(depth_image, -1)

currentCentroid = RetrieveCentroid()
print(distance([-18.25813196715417, -83.9366413712725, 4641.484391419917],[-29.784899111062852, -87.25096953448129, 4943.838039452602]))


# Stop the pipeline
pipeline.stop()
cv2.destroyAllWindows()