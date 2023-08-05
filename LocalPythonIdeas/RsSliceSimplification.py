import cv2
import numpy as np
import pyrealsense2 as rs
import socket
from scipy.ndimage import gaussian_filter
from scipy.linalg import eigvals
import json
import mmap
import struct

def generate_generic(vertices):
    triangles = []
    for i in range(2304-64):
        triangles.append(i)
        triangles.append(i+65)
        triangles.append(i+64)
        triangles.append(i)
        triangles.append(i+1)
        triangles.append(i+65)
    return triangles

def write_to_memory_mapped_file(filtered_cloud, triangles_list, cloud_file_path, triangle_file_path):
    oneDimensionFiltered = [item for sublist in filtered_cloud for item in sublist]
    with open(cloud_file_path, 'w') as file:
        # Write filtered_list to the file
        line = ",".join(str(index) for index in oneDimensionFiltered)
        file.write(line)

    with open(triangle_file_path, 'w') as file:
        # Write triangles_list to the file
        line = ",".join(str(index) for index in triangles_list)
        file.write(line)

def retrieve_base_frame():
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
    # CREATE THE NEW VECTOR3 LIST
    pointCloudVector3 = []
    largest_depth = 0
    for row in range(1, 181):
        for item in range(1, 321):
            tmprow = (row*4)-1
            tmpitem = (item*4)-1
            depth = depth_image[tmprow][tmpitem]
            if(depth > 0 and depth < 10000):
                pixel = [item, row]
                vector = rs.rs2_deproject_pixel_to_point(depth_intrinsics,pixel,depth)
                #newrow.append(vector)
                pointCloudVector3.append(vector)
                if(vector[2]  > largest_depth):
                    largest_depth = vector[2]
        #pointCloudVector3.append(newrow)
    return pointCloudVector3, largest_depth

def downsample_slice(resolution,pcd,largest_depth):
    #DEFINE THE RANGE OF THE SLICING
    new_frame = []
    for i in range(1,resolution+1):
        for pixel in range(0,len(pcd)):
            if round(pcd[pixel][2]) > i*round(largest_depth/resolution)-2 and round(pcd[pixel][2]) < i*round(largest_depth/resolution)+2:
                new_frame.append(pcd[pixel])
        #print(i*round(largest_depth/resolution))
    return new_frame

pcd, largest_depth = retrieve_base_frame()
triangle_list = generate_generic(pcd)
#write_to_memory_mapped_file(pcd, triangle_list, "cloud_mmp.txt", "triangle_mmp.txt")
#print(largest_depth)
#print(len(pcd[0]))
#new_frame = downsample_slice(40,pcd,largest_depth)
write_to_memory_mapped_file(pcd, triangle_list, "cloud_mmp.txt", "triangle_mmp.txt")
#print(new_frame)
#print(len(new_frame))
