import numpy as np
import matplotlib.pyplot as plt

def rotation_matrix(theta_x, theta_y, theta_z):
    Rx = np.array([[1, 0, 0],
                   [0, np.cos(theta_x), -np.sin(theta_x)],
                   [0, np.sin(theta_x), np.cos(theta_x)]])

    Ry = np.array([[np.cos(theta_y), 0, -np.sin(theta_y)],  # Note the negative sign for sin(theta_y)
                   [0, 1, 0],
                   [np.sin(theta_y), 0, np.cos(theta_y)]])

    Rz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                   [np.sin(theta_z), np.cos(theta_z), 0],
                   [0, 0, 1]])

    R = np.dot(Rz, np.dot(Ry, Rx))
    return R

def rotated_point_coordinates(point, theta_x, theta_y, theta_z):
    return np.dot(rotation_matrix(theta_x, theta_y, theta_z), point)

initial_point = np.array([-0.0, -0.0, 0.0])
theta_x = np.radians(60)  # Adjust as needed
theta_y = np.radians(0)  # Adjust as needed
theta_z = np.radians(30)  # Adjust as needed

new_point = rotated_point_coordinates(initial_point, theta_x, theta_y, theta_z)
print(new_point.tolist())
# Visualization
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1, 1, 1])  # Ensures equal aspect ratio

ax.scatter(initial_point[0], initial_point[1], initial_point[2], c='r', marker='o', s=100, label='Initial Point')
ax.scatter(new_point[0], new_point[1], new_point[2], c='g', marker='o', s=100, label='New Point')
ax.scatter(0, 0, 0, c='b', marker='o', s=100, label='Origin')

ax.set_xlabel('X axis (Left/Right)')
ax.set_ylabel('Y axis (Up)')
ax.set_zlabel('Z axis (Forward/Backward)')
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])

# Look down the X-axis with Z going forward
ax.view_init(elev=0, azim=90)  # 0 degrees elevation, 90 degrees azimuth

ax.legend()
plt.show()
