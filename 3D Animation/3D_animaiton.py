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
from ns_open_file import ns_OpenFile
from ns_get_entity_info import ns_GetEntityInfo
from ns_get_analog_info import ns_GetAnalogInfo
from ns_close_file import ns_CloseFile
from ns_get_analog_data import ns_GetAnalogData
from ns_get_analog_data_block import ns_GetAnalogDataBlock
import struct
from scipy.io import loadmat
import math
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from mpl_toolkits.mplot3d import Axes3D
import h5py
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation
import matplotlib
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

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
my_dict = {}
i = -1
for file_path in nc3_files:
    i = i +1
    j = 0
    rec_length = 120
    tmin= 10
    if is_micro[0][j][0][0] == 1:
        sample_rate = 30000
    else:
        sample_rate = 2000
    fileName = os.path.basename(file_path)
    
    min_record=sample_rate * tmin
    max_record = math.floor(min_record+sample_rate*rec_length)
    tmax=max_record/sample_rate    
    # Open the binary file for reading in binary mode ('rb')
    with open(file_path, 'rb') as file:
    # Read the binary data from the file. Start at begining of data with seeek()
        binary_data = file.read()
        file.seek((min_record-1)*2)

    # Create a format string for little-endian unsigned 16-bit integers
    if sample_rate == 2000:
        format_string = '<'+ 'h' * (len(binary_data) // 2)
    else:
        format_string = '<'+ 'f' * (len(binary_data) // 4)

    # Unpack the binary data into a list of integers
    unpacked_data = struct.unpack(format_string, binary_data)

    
    keys.append(fileName[:4])
    samples = [x*conversion[0][j][0][0]+dc_offset[0][j][0][0] for x in unpacked_data[min_record-1:max_record]]
    my_dict.update({keys[i]:samples})
    


        
brain_surface_struct = loadmat('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Surfaces.mat')
brain_surface_content = brain_surface_struct['BrainSurfRaw']
brain_vertices = np.array([brain_surface_content['vertices'][0][0][i] for i in range(len(brain_surface_content['vertices'][0][0]))])
brain_faces = np.array([brain_surface_content['faces'][0][i] for i in range(len(brain_surface_content['faces']))])

#electrodes
#load
with h5py.File('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Electrodes.mat', 'r') as mat_file:

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




fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
#sort bundles


vertices_for_faces = [brain_vertices[face-1] for face in brain_faces[0][:]]

wireframe = Poly3DCollection(vertices_for_faces,facecolors='r', edgecolor='none', alpha=.1)
ax.add_collection3d(wireframe)
#Normalize Sample data
for key in my_dict.keys():
    norm = Normalize(vmin=min(my_dict[key]),vmax=max(my_dict[key]))
    my_dict[key] = norm(my_dict[key])

#sort samples into bundels
def bundle_keys(keys,bundle_dict):
    for key in keys:
        bundle_name = str(key)[:2]
        if bundle_name in bundle_dict:
            bundle_dict[bundle_name].append(key)
        else:
            bundle_dict.update({bundle_name:[key]})
    return bundle_dict

bundle_dict ={}
bundle_keys(my_dict.keys(),bundle_dict)
#colormap
colormap = 'hot'
cmap = plt.get_cmap(colormap)
colormap_dict = {}
def colormap(colormap_dict,cmap,keys,my_dict):
    for key in keys:
        colormap_dict.update({key:cmap(my_dict[key])})
    return colormap_dict
colormap(colormap_dict,cmap,my_dict.keys(),my_dict)



#map electrodes with sample data
f = h5py.File('/mnt/data0/sEEG_DATA/MCW-FH_006/Imaging/Registered DICOM 10 (Meg)/Electrodes.mat','r') 
test = f['ElecMapRaw']
strs=[]
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
    if len(strs[i])==3 and strs[i][0] != "m":
        strs[i] = strs[i][0]+strs[i][1]+"0"+strs[i][2]
electrode_dict = {}
for i in range(len(strs)):
    electrode_dict.update({strs[i]:[elec_x_center[i],elec_y_center[i],elec_z_center[i]]})

elec_radius = 5
u = np.linspace(0, 2 * np.pi, 25)
v = np.linspace(0, np.pi, 25)
electrodes = []
for i in electrode_dict.keys():
    elec_x = elec_radius * np.outer(np.cos(u), np.sin(v)) + electrode_dict[i][0]
    elec_y = elec_radius * np.outer(np.sin(u), np.sin(v)) + electrode_dict[i][1]
    elec_z = elec_radius * np.outer(np.ones(np.size(u)), np.cos(v)) + electrode_dict[i][2]
    electrodes.append(ax.plot_surface(elec_x, elec_y, elec_z, color='b', alpha=0.5))
print(electrodes[0])
#electrodes is in order of electrode_dict
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_zlabel('Z-axis')


#make line between eletrode ends
def update(frame):
    #with t step update the color of the spheres with respect to their LA##
    fps = 30 
    t_step = round(1/((1/sample_rate)/(1/fps)),2)
    t = int(t_step*(frame+1))
   
    j = 0
    for i in electrode_dict.keys():
        if 'm' in i:
            print("no micro")
        else:
            electrode_cmap = colormap_dict[i]
            new_color_values = electrode_cmap[t]
            electrode_obj = electrodes[j]
            
            electrode_obj.set_color(new_color_values)
            j = 1+j

    print("frame")
    return
ani = FuncAnimation(fig, update, frames=100, interval = 1000/30)
output_file = 'frames/frames.gif'
ani.save(output_file, writer='pillow')

plt.show()