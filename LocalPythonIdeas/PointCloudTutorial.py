import numpy as np
import matplotlib.pyplot as plt
import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(depth_frame.get_data())
        colorizer = rs.colorizer()
        colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())

        fig, ax = plt.subplots()
        ax.imshow(colorized_depth)

        cmap = plt.get_cmap("jet")
        norm = plt.Normalize(vmin=0, vmax=2)
        points = rs.pointcloud()
        points.map_to(color_frame)
        vtx = np.asanyarray(points.calculate(depth_frame).get_vertices())
        vtx = vtx.view(np.float32).reshape(vtx.shape + (-1,))

        ax.scatter(vtx[:, 0], vtx[:, 1], c=vtx[:, 2], cmap=cmap, norm=norm, s=1)
        ax.set_xlim(0, 640)
        ax.set_ylim(480, 0)
        plt.show()

except KeyboardInterrupt:
    pass

finally:
    pipeline.stop()