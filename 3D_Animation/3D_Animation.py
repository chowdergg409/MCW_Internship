from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import h5py
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize
import math
from scipy.io import loadmat
import matplotlib.pyplot as plt
import base64
import numpy as np
from mpl_toolkits import mplot3d
from scipy import signal
import sys
import os
from scipy.io import netcdf
import glob
import struct
sys.path.append('/home/hauderc/Documents/GitHub/codes_emu/neuroshare/python')
from ns_get_analog_data_block import ns_GetAnalogDataBlock
from ns_get_analog_data import ns_GetAnalogData
from ns_close_file import ns_CloseFile
from ns_get_analog_info import ns_GetAnalogInfo
from ns_get_entity_info import ns_GetEntityInfo
from ns_open_file import ns_OpenFile
# Load the MATLAB .mat file
mat_contents = loadmat('/home/hauderc/Documents/Test2/run/NSx.mat')

# Access the struct in the loaded data
mat_struct = mat_contents['NSx']

# Access specific fields within the struct
conversion = mat_struct['conversion']
dc_offset = mat_struct['dc']
is_micro = mat_struct['is_micro']

folder_path = '/home/hauderc/Documents/Test2/run'
nc3_files = []
# Use glob to find files with the ".NC3" extension
search_pattern = os.path.join(folder_path, '*.NC3')
nc3_files = glob.glob(search_pattern)
nc3_files = sorted(nc3_files, key=lambda x: os.path.basename(x))
keys = []
raw_dict = {}
power_dict = {}
i = -1
for file_path in nc3_files:
    i = i + 1
    j = 0
    rec_length = 120
    tmin = 10
    if is_micro[0][j][0][0] == 1:
        sample_rate = 30000
    else:
        sample_rate = 2000
    fileName = os.path.basename(file_path)

    min_record = sample_rate * tmin
    max_record = math.floor(min_record + sample_rate * rec_length)
    tmax = max_record / sample_rate
    # Open the binary file for reading in binary mode ('rb')
    with open(file_path, 'rb') as file:
        # Read the binary data from the file. Start at begining of data with
        # seeek()
        binary_data = file.read()
        file.seek((min_record - 1) * 2)

    # Create a format string for little-endian unsigned 16-bit integers
    if sample_rate == 2000:
        format_string = '<' + 'h' * (len(binary_data) // 2)
    else:
        format_string = '<' + 'f' * (len(binary_data) // 4)

    # Unpack the binary data into a list of integers
    unpacked_data = struct.unpack(format_string, binary_data)

    # update raw dictionary and power dictionary. Raw dictionary will be used
    # for 2D graphs, and Power dictionary will be normalized and used for the
    # 3D animation
    keys.append(fileName[:4])
    raw_samples = [x * conversion[0][j][0][0] + dc_offset[0][j][0][0]
                   for x in unpacked_data[min_record - 1:max_record]]
    power_samples = [raw_samples[i]**2 for i in range(len(raw_samples))]
    power_dict.update({keys[i]: power_samples})
    raw_dict.update({keys[i]: raw_samples})

brain_surface_struct = loadmat(
    '/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Surfaces.mat')
brain_surface_content = brain_surface_struct['BrainSurfRaw']
brain_vertices = np.array([brain_surface_content['vertices'][0][0][i]
                          for i in range(len(brain_surface_content['vertices'][0][0]))])
brain_faces = np.array([brain_surface_content['faces'][0][i]
                       for i in range(len(brain_surface_content['faces']))])

# electrodes
# load
with h5py.File('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Electrodes.mat', 'r') as mat_file:

    # List all the keys (group names) in the HDF5 structure
    keys = list(mat_file.keys())

    # Access a specific dataset within the file
    dataset = mat_file['ElecXYZRaw']

    # Read the dataset into a NumPy array
    data = dataset[()]

# set varaibles
elec_x_center = data[0]
elec_y_center = data[1]
elec_z_center = data[2]
# Normalize Sample data
for key in power_dict.keys():
    norm = Normalize(vmin=min(power_dict[key]), vmax=max(power_dict[key]))
    power_dict[key] = norm(power_dict[key])

# sort samples into bundels


def bundle_keys(keys, bundle_dict):
    for key in keys:
        bundle_name = str(key)[:2]
        if bundle_name in bundle_dict:
            bundle_dict[bundle_name].append(key)
        else:
            bundle_dict.update({bundle_name: [key]})
    return bundle_dict


bundle_dict = {}
bundle_keys(power_dict.keys(), bundle_dict)

f = h5py.File(
    '/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Electrodes.mat',
    'r')
test = f['ElecMapRaw']
strs = []
for i in range(len(test[0])):
    st = test[0][i]
    obj = f[st]
    chrs = []
    for j in range(len(obj[:])):
        chrs.append(chr(obj[:][j][0]))
    str1 = ""
    for x in range(len(chrs)):
        str1 = str1 + chrs[x]
    strs.append(str1)
for i in range(len(strs)):
    if len(strs[i]) == 3 and strs[i][0] != "m":
        strs[i] = strs[i][0] + strs[i][1] + "0" + strs[i][2]
electrode_dict = {}
for i in range(len(strs)):
    electrode_dict.update(
        {strs[i]: [elec_x_center[i], elec_y_center[i], elec_z_center[i]]})

fig = plt.figure(layout="constrained")

gs = GridSpec(int(len(bundle_dict.keys()) / 2), 4, figure=fig)
axes_dict = {}
ax1 = fig.add_subplot(gs[:, :-2], projection='3d')
axes_dict.update({"ax1": ax1})

vertices_for_faces = [brain_vertices[face - 1] for face in brain_faces[0][:]]

wireframe = Poly3DCollection(
    vertices_for_faces,
    facecolors='b',
    edgecolor='none',
    alpha=.1)
ax1.add_collection3d(wireframe)

# make 2D Bundles plots
i = 0
vertical_lines = []
for bundle in bundle_dict.keys():
    if i < len(bundle_dict.keys()) / 2:
        ax_i = fig.add_subplot(gs[i, 2])
    else:
        ax_i = fig.add_subplot(gs[i - int(len(bundle_dict.keys()) / 2), 3])
    axes_dict.update({"ax%s" % (str(key)): ax_i})
    for key in bundle_dict[bundle]:
        x = [i / sample_rate for i in range(len(raw_dict[key]))]
        y = raw_dict[key]
    ax_i.plot(x, y)
    ax_i.set_title(str(bundle))
    ax_i.set_xlabel("time")
    ax_i.set_ylabel("micro V")
    vertical_lines.append(ax_i.axvline(x=0, color='red', linestyle='--'))
    i = i + 1

# colormap
colormap = 'hot'
cmap = plt.get_cmap(colormap)
colormap_dict = {}


def colormap(colormap_dict, cmap, keys, power_dict):
    for key in keys:
        colormap_dict.update({key: cmap(power_dict[key])})
    return colormap_dict


colormap(colormap_dict, cmap, power_dict.keys(), power_dict)

elec_radius = 2
u = np.linspace(0, 2 * np.pi, 25)
v = np.linspace(0, np.pi, 25)
electrodes = []
for i in electrode_dict.keys():
    elec_x = elec_radius * np.outer(np.cos(u),
                                    np.sin(v)) + electrode_dict[i][0]
    elec_y = elec_radius * np.outer(np.sin(u),
                                    np.sin(v)) + electrode_dict[i][1]
    elec_z = elec_radius * \
        np.outer(np.ones(np.size(u)), np.cos(v)) + electrode_dict[i][2]
    electrodes.append(
        ax1.plot_surface(
            elec_x,
            elec_y,
            elec_z,
            color='b',
            alpha=0.5))
print(electrodes[0])
# electrodes is in order of electrode_dict
ax1.set_xlabel('X-axis')
ax1.set_ylabel('Y-axis')
ax1.set_zlabel('Z-axis')


def update(frame):
    # with t step update the color of the spheres with respect to their LA##
    fps = 30
    idx_step = round(1 / ((1 / sample_rate) / (1 / fps)), 2)
    idx = int(idx_step * (frame + 1))
    t = (1/sample_rate)*idx
    j = 0
    print(electrode_dict.keys())
    for i in electrode_dict.keys():
        if 'm' in i:
            print("no micro")
        else:
            electrode_cmap = colormap_dict[i]
            new_color_values = electrode_cmap[idx]
            electrode_obj = electrodes[j]

            electrode_obj.set_color(new_color_values)
            j = 1 + j
        
    
    for i in axes_dict.keys():
        if 'ax1' in i:
            continue
        else:
            for line in vertical_lines:
                line.set_xdata(t)
        

    print("frame")
    return


ani = FuncAnimation(fig, update, frames=100, interval=1000 / 30)
output_file = 'frames/frames.gif'
# ani.save(output_file, writer='pillow')

plt.show()
