import numpy as np
from sklearn.linear_model import LinearRegression
import pyrealsense2 as rs
import cv2
import math

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
    depth_image = cv2.flip(depth_image,-1)
    depth_intrinsics = frames.profile.as_video_stream_profile().intrinsics
    # CREATE THE NEW VECTOR3 LIST
    pointCloudVector3 = []
    for row in range(0, 720):
        for item in range(0, 1280):
            depth = depth_image[row][item]
            if(depth > 0 and depth < 10000):
                pixel = [item, row]
                vector = rs.rs2_deproject_pixel_to_point(depth_intrinsics,pixel,depth)
                #print(vector)
                pointCloudVector3.append(vector)
            else:
                vector = [0,0,0]
                pointCloudVector3.append(vector)
    return pointCloudVector3

def fit_plane_center(points):
    # Convert points to 2D numpy array
    points = np.array(points, dtype=float)
    # Perform linear regression to fit a plane
    model = LinearRegression()
    model.fit(points[:, :2], points[:, 2])

    # Calculate the center of the bounding box
    x_center = (points[:, 0].min() + points[:, 0].max()) / 2
    y_center = (points[:, 1].min() + points[:, 1].max()) / 2
    a, b = model.coef_
    d = model.intercept_
    z_center = a * x_center + b * y_center + d

    return [x_center, y_center, z_center]

def fit_plane(points):
    points = np.array(points)
    # Separate coordinates
    xs = points[:, 0]
    ys = points[:, 1]
    zs = points[:, 2]

    # Perform linear regression to fit a plane
    model = LinearRegression()
    model.fit(np.column_stack((xs, ys)), zs)

    # Calculate the z-coordinates of the corners of the bounding box
    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()
    a, b = model.coef_
    d = model.intercept_
    z1 = a * x_min + b * y_min + d
    z2 = a * x_min + b * y_max + d
    z3 = a * x_max + b * y_min + d
    z4 = a * x_max + b * y_max + d

    return [[x_min, y_min, z1], [x_min, y_max, z2], [x_max, y_min, z3], [x_max, y_max, z4]]

def write_to_memory_mapped_file(filtered_cloud, triangles_list, cloud_file_path, triangle_file_path):
    try:
        oneDimensionFiltered = [item for sublist in filtered_cloud for item in sublist]
        with open(cloud_file_path, 'w') as file:
            # Write filtered_list to the file
            line = ",".join(str(index) for index in oneDimensionFiltered)
            file.write(line)

        with open(triangle_file_path, 'w') as file:
            # Write triangles_list to the file
            line = ",".join(str(index) for index in triangles_list)
            file.write(line)
    except Exception as e:
        with open("error_log.txt", "w") as error_file:
            error_file.write(str(e))

def filter_out_null(blocks):
    filtered_array = []
    for i in range(0,200):
        filtered_block = []
        for point in blocks[i]:
            if point[2] != 0:
                filtered_block.append(point)
        filtered_array.append(filtered_block)
    return filtered_array

def chunk(pcd):
    chunk_list = []
    for chunkrow in range(0, 10):
        for chunkcol in range(0,20):
            chunk = []
            for row in range(0, 72):
                for column in range(0,64):
                    chunk.append(pcd[
                                    (chunkrow*92160)+
                                    (row*1280)+
                                    (chunkcol*64)+
                                    (column)])
            chunk_list.append(chunk)
    return chunk_list

def generate_triangles():
    triangles = []
    for row in range(0, 9):
        for col in range(0, 19):
            triangles.append((row * 20) +
                             (col))
            triangles.append((row * 20) +
                             (col) + 10)
            triangles.append((row * 20) +
                             (col) + 1)
            # Second Triangle
            triangles.append((row * 20) +
                             (col) + 1)
            triangles.append((row * 20) +
                             (col) + 19)
            triangles.append((row * 20) +
                             (col) + 20)
    return triangles

def main():
    pcd = retrieve_base_frame()
    reshaped_array = chunk(pcd)
    #print(len(reshaped_array))
    #FILTER OUT THE NULLS PUT EARLIER
    filtered_array = filter_out_null(reshaped_array)
    #print(len(filtered_array))
    #print(len(filtered_array[0][0]))
    cloud_file_path = "PythonFiles/temp/cloud_mmp.txt"
    triangle_file_path = "PythonFiles/temp/triangle_mmp.txt"
    triangles_list = generate_triangles()
    #print(filtered_array)
    #print(len(filtered_array))
    simplifiedPCD = []
    for region in range(0,200):
        if (filtered_array[region] != []):
            simplifiedPCD.append(fit_plane_center(filtered_array[region]))
    write_to_memory_mapped_file(simplifiedPCD,triangles_list,cloud_file_path,triangle_file_path)

if __name__ == "__main__":
    main()





