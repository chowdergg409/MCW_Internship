import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.io import loadmat
import h5py
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize

brain_surface_struct = loadmat('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered/Surfaces.mat')
brain_surface_content = brain_surface_struct['BrainSurfRaw']
brain_vertices = np.array([brain_surface_content['vertices'][0][0][i] for i in range(len(brain_surface_content['vertices'][0][0]))])
brain_faces = np.array([brain_surface_content['faces'][0][i] for i in range(len(brain_surface_content['faces']))])
print(brain_vertices)
print(brain_faces[0])
#electrodes
#load
with h5py.File('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered/Electrodes.mat', 'r') as mat_file:

    # List all the keys (group names) in the HDF5 structure
    keys = list(mat_file.keys())

    # Access a specific dataset within the file
    dataset = mat_file['ElecXYZRaw']

    # Read the dataset into a NumPy array
    data = dataset[()]

#set varaibles
elec_x_center = data[0]
elec_y_center = data[1]
elec_z_center = data[2]
#make electrode shapes
elec_radius = 5
u = np.linspace(0, 2 * np.pi, 25)
v = np.linspace(0, np.pi, 25)



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(len(elec_x_center)):
    elec_x = elec_radius * np.outer(np.cos(u), np.sin(v)) + elec_x_center[i]
    elec_y = elec_radius * np.outer(np.sin(u), np.sin(v)) + elec_y_center[i]
    elec_z = elec_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + elec_z_center[i]
    ax.plot_surface(elec_x, elec_y, elec_z, color='b', alpha=0.5)

vertices_for_faces = [brain_vertices[face-1] for face in brain_faces[0][:]]

wireframe = Poly3DCollection(vertices_for_faces, facecolors = 'r',edgecolor='none', alpha=.1)
ax.add_collection3d(wireframe)
#Normalize Sample data
    
norm = Normalize(vmin=data.min(), vmax=data.max())
#identify electrodes with sample data


def update(frame):
    #with t step update the color of the spheres with respect to their LA##
    print("frame")
    return
ani = FuncAnimation(fig, update, frames=100)

plt.show()


