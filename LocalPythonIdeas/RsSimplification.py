import pyrealsense2 as rs
import numpy as np
import open3d as o3d
import socket

def get_depth_frames():
    # Create pipeline and configure it
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

    # Start pipeline
    pipeline.start(config)

    try:
        # Wait for the next frameset
        frames = pipeline.wait_for_frames()

        # Get depth frame
        depth_frame = frames.get_depth_frame()

        # Convert depth frame to a numpy array
        depth_image = np.asanyarray(depth_frame.get_data())

    finally:
        # Stop the pipeline and release resources
        pipeline.stop()

    return depth_image

# Function to simplify point cloud
def simplify_point_cloud(points, target_num_points):
    # Ensure points are of type numpy.ndarray with dtype float64
    points = np.array(points, dtype=np.float64)

    # Create an Open3D point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Simplify the point cloud using vertex clustering
    pcd_simplified, _ = pcd.simplify_vertex_clustering(target_num_points)

    # Convert the simplified point cloud back to a numpy array
    simplified_points = np.asarray(pcd_simplified.points)

    return simplified_points

def main():
    udp_host = "127.0.0.1"
    udp_port = 5052

    # Retrieve depth frames from RealSense D415
    depth_image = get_depth_frames()

    # Create a point cloud from the depth image
    intrinsic = o3d.camera.PinholeCameraIntrinsic(
        width=depth_image.shape[1],
        height=depth_image.shape[0],
        fx=617.306,  # Update with your camera intrinsic parameters
        fy=617.714,
        cx=328.083,
        cy=241.447
    )
    pcd = o3d.geometry.PointCloud.create_from_depth_image(
        o3d.geometry.Image(depth_image),
        intrinsic
    )

    # Visualize the original point cloud (optional)
    o3d.visualization.draw_geometries([pcd], window_name="Original Point Cloud")

    # Simplify the point cloud using voxel downsampling
    voxel_size = 0.01  # Adjust this value based on your desired simplification level
    pcd_downsampled = pcd.voxel_down_sample(voxel_size)

    # Convert the downsampled point cloud back to a numpy array
    simplified_points = np.asarray(pcd_downsampled.points)

    # Visualize the simplified point cloud (optional)
    #o3d.visualization.draw_geometries([pcd_downsampled], window_name="Simplified Point Cloud")

    # Convert the numpy array to a bytes object
    serialized_data = simplified_points.tobytes()

    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send the data to Unity
    server_socket.sendto(serialized_data, (udp_host, udp_port))

if __name__ == "__main__":
    main()
