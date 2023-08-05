import random
import open3d as o3d
import cv2
import numpy as np
import pyrealsense2 as rs
import socket

# Create pipeline and configure it
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# Start pipeline
pipeline.start(config)

# Wait for the next frameset
frames = pipeline.wait_for_frames()

# Get depth frame
depth_frame = frames.get_depth_frame()
# Convert depth frame to a numpy array
depth_image = np.asanyarray(depth_frame.get_data())
depth_intrinsics = frames.profile.as_video_stream_profile().intrinsics

#Sockets and Ports
udp_host = "127.0.0.1"
udp_port = 5052

#CREATE THE NEW VECTOR3 LIST
pointCloudVector3 = []
for row in range(0,720):
    for item in range(0,1280):
        depth = depth_image[row][item]
        if len(pointCloudVector3) == 0:
            pixel = [item, row]
            pointCloudVector3.append(rs.rs2_deproject_pixel_to_point(depth_intrinsics, pixel, depth))
        else:
            if depth > 0 and (item*row)%9216 == 0:
                pixel = [item,row]
                pointCloudVector3.append(rs.rs2_deproject_pixel_to_point(depth_intrinsics,pixel,depth))

print(pointCloudVector3)

simplified_points = np.array(pointCloudVector3)

# Convert the numpy array to a bytes object
serialized_data = simplified_points.tobytes()

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send the data to Unity
server_socket.sendto(serialized_data, (udp_host, udp_port))
pipeline.stop()