import cv2
import numpy as np
import pyrealsense2 as rs
import socket
from scipy.ndimage import gaussian_filter
from scipy.linalg import eigvals
import json
import mmap
import struct

#Create a hessian matrix to find which points have most curvature
def hessian_matrix(point_cloud, sigma=1.0):
    # Convert the input point cloud list to a NumPy array for easier manipulation
    point_cloud = np.array(point_cloud)

    # Calculate the gradient using finite differences
    gradient_x = np.gradient(point_cloud[:, 0])
    gradient_y = np.gradient(point_cloud[:, 1])
    gradient_z = np.gradient(point_cloud[:, 2])

    # Calculate the Hessian matrix using finite differences
    hessian_xx = np.gradient(gradient_x)
    hessian_xy = np.gradient(gradient_y, axis=0)  # Gradient of the y-gradient w.r.t x
    hessian_xz = np.gradient(gradient_z, axis=0)  # Gradient of the z-gradient w.r.t x
    hessian_yy = np.gradient(gradient_y, axis=0)  # Gradient of the y-gradient w.r.t y
    hessian_yz = np.gradient(gradient_z, axis=0)  # Gradient of the z-gradient w.r.t z (with respect to the index)
    hessian_zz = np.gradient(gradient_z, axis=0)  # Second derivative of the z-gradient w.r.t z

    # Create the Hessian matrix (3x3xN) by stacking the components
    hessian = np.stack((hessian_xx, hessian_xy, hessian_xz,
                        hessian_xy, hessian_yy, hessian_yz,
                        hessian_xz, hessian_yz, hessian_zz), axis=-1)

    return hessian, point_cloud

#Getting Eigenvalues will yield an absolute value that determines the extremity of local curvature
def local_curvature(hessian_matrix):
    num_points = len(hessian_matrix)
    curvature = np.zeros(num_points)

    for i in range(num_points):
        hessian_i = [[],[],[]]
        for xyz in range(0,3):
            for item in range(0, 3):
                hessian_i[xyz].append(hessian[i][xyz*3+item])
        eigenvalues = np.abs(np.linalg.eigvals(hessian_i))
        curvature[i] = np.max(eigenvalues)

    return curvature

def filter_extremities(egvalues,smoothed_cloud):
    filtered_cloud = []
    for i in range(len(egvalues)):
        if(egvalues[i] > 1200):
            filtered_item = []
            filtered_item.append(smoothed_cloud[i][0])
            filtered_item.append(smoothed_cloud[i][1])
            filtered_item.append(smoothed_cloud[i][2])
            filtered_cloud.append(filtered_item)
    return filtered_cloud

def generate_triangles(vertices):
    triangles = []
    for i in range(len(vertices)):
        if i <= len(vertices)-3:
            triangles.append(i)
            triangles.append(i+1)
            triangles.append(i+2)
    return triangles

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

#CREATE THE NEW VECTOR3 LIST
pointCloudVector3 = []
for row in range(0,720):
    for item in range(0,1280):
        depth = depth_image[row][item]
        '''
        if len(pointCloudVector3) == 0:
            pixel = [item, row]
            pointCloudVector3.append(rs.rs2_deproject_pixel_to_point(depth_intrinsics, pixel, depth))
        else:
            if depth > 0 and (item*row)%200 == 0:
                pixel = [item,row]
                pointCloudVector3.append(rs.rs2_deproject_pixel_to_point(depth_intrinsics,pixel,depth))
        '''
        if (item*row)%400 == 0:
            pixel = [item, row]
            pointCloudVector3.append(rs.rs2_deproject_pixel_to_point(depth_intrinsics, pixel, depth))

#Calculating the hessian matrix
hessian,smoothed_cloud = hessian_matrix(pointCloudVector3, sigma=1.0)

#Calculating the local curvature
curves = local_curvature(hessian)

'''
#Get a filtered cloud with edge detection
filtered_cloud = filter_extremities(curves,smoothed_cloud)

#Triangles list creation
triangles_list = generate_triangles(filtered_cloud)
'''

#WE'RE GOING BACK TO BASICS
#triangles_list = generate_triangles(pointCloudVector3)
triangles_list = generate_generic(pointCloudVector3)
#Shared memory
triangle_file_path = "triangle_mmp.txt"
cloud_file_path = "cloud_mmp.txt"
write_to_memory_mapped_file(pointCloudVector3,triangles_list,cloud_file_path,triangle_file_path)
pipeline.stop()
