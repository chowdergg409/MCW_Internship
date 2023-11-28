from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
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
import open3d as o3d
sys.path.append('/home/hauderc/Documents/GitHub/codes_emu/neuroshare/python')
from ns_get_analog_data_block import ns_GetAnalogDataBlock
from ns_get_analog_data import ns_GetAnalogData
from ns_close_file import ns_CloseFile
from ns_get_analog_info import ns_GetAnalogInfo
from ns_get_entity_info import ns_GetEntityInfo
from ns_open_file import ns_OpenFile
import tkinter as tk
from tkinter import filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import rand

from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
import csv

selected_folder = {"folder":""}
t_values = {"t_event": "", "t_end": "", "t_start": ""}
selected_date = ""

def open_folder_dialog():
    folder_path = filedialog.askdirectory(title="select a folder")
    if folder_path:
        print(folder_path)
        selected_folder["folder"] = folder_path
        folder_path_entry.delete(0, tk.END)
        folder_path_entry.insert(0, folder_path)
        print(f"Selected folder: {folder_path}")


def get_selected_date():
    selected_date = cal.get_date()
    print(f"Selected date: {selected_date}")

def confirm_and_exit():
    t_values["t_event"] = t_event.get()
    t_values["t_end"] = t_end.get()
    t_values["t_start"] = t_start.get()
    print("Entry values:", t_values)
    window.destroy()

# Create the main window
window = tk.Tk()
window.title("Folder Selector with Date Picker")

# Create three text entry boxes
folder_path_label = tk.Label(window, text="folderpath with NC3's:")
folder_path_label.pack()

folder_path_entry = tk.Entry(window, width=40)
folder_path_entry.pack(pady=10)

t_event_label = tk.Label(window, text="Time of event(hh:mm:ss):")
t_event_label.pack()

t_event = tk.Entry(window, width=40)
t_event.pack(pady=10)

t_end_label = tk.Label(window, text="Time after in minutes:")
t_end_label.pack()

t_end = tk.Entry(window, width=40)
t_end.pack(pady=10)

t_start_label = tk.Label(window, text="Time before in minutes:")
t_start_label.pack()

t_start = tk.Entry(window, width=40)
t_start.pack(pady=10)

# Create a button to open the file dialog
button = tk.Button(window, text="Open Folder", command=open_folder_dialog)
button.pack(pady=20)

# Create a DateEntry widget for date selection
date_label = tk.Label(window, text="Select a Date:")
date_label.pack()

cal = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2)
cal.pack(pady=10)

# Create a button to get the selected date
date_button = tk.Button(window, text="Get Date", command=get_selected_date)
date_button.pack(pady=20)

confirm_button = tk.Button(window, text="Confirm and Exit", command=confirm_and_exit)
confirm_button.pack(pady=20)

# Run the GUI
window.mainloop()

#hours mins sec string converter
def hms_to_seconds(time_string):
    hours, minutes, seconds = map(int, time_string.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

#saves current folder as a csv to be referenced for later
def list_folder_contents(folder_path, csv_writer):
    # Get a list of all files and subdirectories in the folder
    entries = os.listdir(folder_path)

    # Write the entries to the CSV file
    for entry in entries:
        entry_path = os.path.join(folder_path, entry)

        if os.path.isdir(entry_path):
            # If the entry is a subfolder, recursively list its contents
            list_folder_contents(entry_path, csv_writer)
        else:
            # If the entry is a file, write it to the CSV file
            csv_writer.writerow([entry_path])
directory = []
def create_folder_contents_csv(root_folder_path):
    # Create a CSV file to store the entries
    csv_file_path = 'folder_contents.csv'

    # Check if the file already exists
    if os.path.exists(csv_file_path):
        print("CSV file already exists. Exiting.")
       # with open(csv_file_path, 'r') as csvfile:
       #     csv_reader = csv.reader(csvfile)
       # for row in csv_reader:
       #     directory.append(row)
       #     print(row)
        return #directory

    # Write the entries to the CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Entry'])

        # Call the function to list folder contents and save to CSV
        list_folder_contents(root_folder_path, csv_writer)

    print(f"CSV file '{csv_file_path}' created successfully.")

# Call the function to list folder contents and save to CSV
create_folder_contents_csv(selected_folder['folder'])
print(directory)
#t_event = 2160
t_event = t_values['t_event']
#t_start = t_event - 120
print(t_values['t_start'])
#t_end = t_event+120
print(t_values['t_end'])
print(selected_date)
# Load the MATLAB .mat file
mat_contents = loadmat('/home/hauderc/Documents/Test_seizure/run/NSx.mat')

# Access the struct in the loaded data
mat_struct = mat_contents['NSx']

# Access specific fields within the struct
conversion = mat_struct['conversion']
dc_offset = mat_struct['dc']
is_micro = mat_struct['is_micro']

folder_path = '/home/hauderc/Documents/Test_seizure/run'
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
    rec_length = 3600
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
# Create an Open3D TriangleMesh
mesh = o3d.geometry.TriangleMesh()
mesh.vertices = o3d.utility.Vector3dVector(brain_vertices)
mesh.triangles = o3d.utility.Vector3iVector(brain_faces[0]-1)
# Get the number of triangles in the original mesh
original_triangle_count = len(np.asarray(mesh.triangles))
# Specify the target number of triangles after simplification
target_triangle_count = int(original_triangle_count * 0.001)  # Adjust the factor as needed
# Simplify the mesh using quadric edge collapse decimation
simplified_mesh = mesh.simplify_quadric_decimation(target_triangle_count)
# Get the simplified vertices and faces
simplified_vertices = np.asarray(simplified_mesh.vertices)
simplified_faces = np.asarray(simplified_mesh.triangles)
simplified_triangles = [simplified_vertices[triangle] for triangle in simplified_faces]

idx_start = t_start*sample_rate
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

#Channel selection Menu
def move_selected_entry():
    selected_index = listbox.curselection()
    if selected_index:
        selected_value = listbox.get(selected_index)
        listbox.delete(selected_index)
        listbox_right.insert(tk.END, selected_value)

# Create the main window
window = tk.Tk()
window.title("Entry Mover")

# Create a left scrollable box
listbox_frame_left = tk.Frame(window)
listbox_frame_left.pack(side=tk.LEFT, padx=10, pady=10)

listbox_scroll_left = tk.Scrollbar(listbox_frame_left, orient=tk.VERTICAL)
listbox = tk.Listbox(listbox_frame_left, selectmode=tk.SINGLE, yscrollcommand=listbox_scroll_left.set)

listbox_scroll_left.config(command=listbox.yview)
listbox_scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Populate the left listbox with sample entries
for key in bundle_dict.keys():
    listbox.insert(tk.END, key)

# Create a button to move selected entry to the right
move_button = tk.Button(window, text="Move >>", command=move_selected_entry)
move_button.pack(pady=10)

# Create a right scrollable box
listbox_frame_right = tk.Frame(window)
listbox_frame_right.pack(side=tk.LEFT, padx=10, pady=10)

listbox_scroll_right = tk.Scrollbar(listbox_frame_right, orient=tk.VERTICAL)
listbox_right = tk.Listbox(listbox_frame_right, selectmode=tk.SINGLE, yscrollcommand=listbox_scroll_right.set)

listbox_scroll_right.config(command=listbox_right.yview)
listbox_scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
listbox_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Run the GUI
window.mainloop()

fig = plt.figure(layout="constrained")

gs = GridSpec(int(len(bundle_dict.keys()) / 2), 4, figure=fig)
axes_dict = {}
ax1 = fig.add_subplot(gs[:, :-2], projection='3d', picker = True)
axes_dict.update({"ax1": ax1})


wireframe = Poly3DCollection(
    simplified_triangles,
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
u = np.linspace(0, 2 * np.pi, 5)
v = np.linspace(0, np.pi, 5)
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
            alpha=0.5,
            label=str(i)))

# electrodes is in order of electrode_dict
ax1.set_xlabel('X-axis')
ax1.set_ylabel('Y-axis')
ax1.set_zlabel('Z-axis')

def onpick(event):
    if isinstance(event.artist, Line3DCollection):
        thisSphere = event.artist
        label = thisSphere.get_label()
        print(str(label))

fps = 30
def update(frame):
    # with t step update the color of the spheres with respect to their LA##
    idx_step = round(1 / ((1 / sample_rate) / (1 / fps)), 2)
    idx = int(idx_step * (frame + 1)+idx_start)
    t = (1/sample_rate)*idx + t_start
    j = 0
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

fig.canvas.mpl_connect('pick event', onpick)
ani = FuncAnimation(fig, update, frames=(t_end-t_start)*fps, interval=1000 / 30)
output_file = 'frames/frames.gif'
#ani.save(output_file, writer='pillow')

plt.show()
