import numpy as np
import cv2
import pyrealsense2 as rs

def compute_disparity(left_img, right_img, num_disparities=64, block_size=15):
    stereo = cv2.StereoBM_create(numDisparities=num_disparities, blockSize=block_size)
    disparity = stereo.compute(left_img, right_img)
    return disparity

def main():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
    config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)

    # Start streaming
    pipeline.start(config)

    try:
        while True:
            # Get frames
            frames = pipeline.wait_for_frames()
            left_ir_frame = frames.get_infrared_frame(1)
            right_ir_frame = frames.get_infrared_frame(2)

            # Convert images to numpy arrays
            left_ir_image = np.asanyarray(left_ir_frame.get_data())
            right_ir_image = np.asanyarray(right_ir_frame.get_data())

            # Compute disparity
            disparity = compute_disparity(left_ir_image, right_ir_image)

            # Display images
            cv2.imshow('Left IR', left_ir_image)
            cv2.imshow('Right IR', right_ir_image)
            cv2.imshow('Disparity', disparity)

            # Break the loop on 'esc' key press
            if cv2.waitKey(1) == 27:
                break

    finally:
        # Stop streaming
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()