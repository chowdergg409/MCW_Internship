# Author: Connor Hauder
# Date: 1 Deceomber 2023
from matplotlib.gridspec import GridSpec
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib
from matplotlib import cm
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
import sys ; sys.path.append('/home/hauderc/Documents/GitHub/codes_emu/neuroshare/python')
import os
from scipy.io import netcdf
import glob
import struct
import open3d as o3d
from ns_get_analog_data_block import ns_GetAnalogDataBlock
from ns_get_analog_data import ns_GetAnalogData
from ns_close_file import ns_CloseFile
from ns_get_analog_info import ns_GetAnalogInfo
from ns_get_entity_info import ns_GetEntityInfo
from ns_open_file import ns_OpenFile
from ns_get_file_info import ns_GetFileInfo
import tkinter as tk
from tkinter import filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import rand
from pathlib import Path
from typing import List
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
import csv
from datetime import datetime, timedelta
from matplotlib.widgets import Button
#gloval dict for functions
globals_dict = {"selected folder": None,
                "t_event":None, 't_after_event': None, 't_before_event':None,
                "selected date":None,
                "selected file":None,
                "enter time":None,
                "selected case": None,
                "nf3_files":None,
                "rec_length": None,
                "rec_length_1": None,
                "rec_length_2": None,
                "Nsx_filepath": None,
                "nf3_index_dict": None,
                'first_rec_length':None,
                'nev_files':None,
                't_start_1':None,
                't_start_2':None,
                't_end_1': None,
                't_end_2': None,
                'NC3_folder_path': None,
                'NC3_folder_pathes': None,
                'brain_surface_path': None,
                'simplified_verticies': None,
                'simplified_faces': None,
                'simplified_triangles': None,
                'electrode_path':None,
                'elec_x_center':None,
                'elec_y_center':None,
                'elec_z_center': None,
                'listbox':None,
                'listbox_right':None,
                'sample_rate': None,
                'toggle_LH': False,
                'toggle_RH':False,
                'selected_channels':[]}

datetime_dict = {"event_start_datetime":None,"event_end_datetime":None,"event_datetime":None}
nev_dict = {}
raw_dict = {}
power_dict = {}
bundle_dict = {}
electrode_dict = {}

def get_selected_file():
    file_path = filedialog.askopenfilename(title="select a .nev file", filetypes=[("nev files","*.nev")])
    globals_dict["selected file"] = file_path
    globals_dict["selected case"] = 'case1'
    window.destroy()


def get_enter_time():
    globals_dict["enter time"] = True
    globals_dict["selected case"] = 'case2'
    window.destroy()

def get_Nsx():
    file_path = filedialog.askopenfilename(title="select the Nsx.mat file", filetypes=[("MAT files","*.mat")])
    globals_dict["Nsx_filepath"] = file_path

def get_rec_legnth(nf3_files):
    #might not work look at the min and max items this is jank
    for nf3 in nf3_files:
        string_of_filepath = nf3
        index_of_run = string_of_filepath.find("run-")
        if index_of_run != -1 and index_of_run + len("run-") < len(string_of_filepath):
            next_two_characters = string_of_filepath[index_of_run + len("run-"):index_of_run + len("run-") + 2]
            globals_dict['nf3_index_dict'].update({nf3:int(next_two_characters)})
    print(globals_dict['nf3_index_dict'].items())
    index = []
    for item in globals_dict['nf3_index_dict'].item():
        index.append(item[1])
    min_item = min(int(index), key=lambda x: x[1])
    max_item = max(int(index), key=lambda x: x[1])
    for item in globals_dict['nf3_index_dict'].items():
        if min_item in item:
            file_path = globals_dict['nf3_index_dict'][min_item]
            file_path = file_path[:-3]+'nev'
            nsResult, fileInfo = ns_GetFileInfo(file_path)
            globals_dict['first_rec_length'] = fileInfo['TimeSpan']
        if max_item in item:
            file_path = globals_dict['nf3_index_dict'][max_item]
            file_path = file_path[:-3]+'nev'
            nsResult, fileInfo = ns_GetFileInfo(file_path)
            globals_dict['last_rec_length'] = fileInfo['TimeSpan']
            
    
# Create the main window
def ui_case1():
    print(globals_dict["selected file"])

def ui_case2():
    def open_folder_dialog():
        folder_path = filedialog.askdirectory(title="select a folder")
        if folder_path:
            print(folder_path)
            globals_dict["selected folder"] = folder_path
            folder_path_entry.delete(0, tk.END)
            folder_path_entry.insert(0, folder_path)
            print(f"Selected folder: {folder_path}")


    def get_selected_date():
        globals_dict["selected date"] = cal.get_date()
        print(f"Selected date: {globals_dict['selected date']}")

    def confirm_and_exit():
        globals_dict["t_event"] = t_event.get()
        globals_dict['t_after_event'] = t_end.get()
        globals_dict['t_before_event'] = t_start.get()
        print("Entry values:", globals_dict['t_after_event'],globals_dict['t_event'],globals_dict['t_before_event'])
        window.destroy()

    window = tk.Tk()
    window.title("Folder Selector with Date Picker")
    # Create three text entry boxes
    folder_path_label = tk.Label(window, text="folderpath with .nev's and .nf3's:")
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
    date_label = tk.Label(window, text="Select Date of Event:")
    date_label.pack()

    cal = DateEntry(window, width=12, background='darkblue', foreground='white', borderwidth=2)
    cal.pack(pady=10)

    # Create a button to get the selected date
    date_button = tk.Button(window, text="Get Date", command=get_selected_date)
    date_button.pack(pady=20)

    confirm_button = tk.Button(window, text="Confirm and Exit", command=confirm_and_exit)
    confirm_button.pack(pady=20)

    window.mainloop()

# Run the GUI
def default():
    print("No Selection")

def initialize_case1():
    nsResult, hFile = ns_OpenFile(globals_dict["selected file"], 'single')
    nsResult, fileInfo = ns_GetFileInfo(hFile)
    nsResult = ns_CloseFile(hFile)
    seconds = fileInfo['Time_Sec']
    minutes = fileInfo['Time_Min']
    hours = fileInfo['Time_Hour']
    day = fileInfo['Time_Day']
    month = fileInfo['Time_Month']
    year = fileInfo['Time_Year']
    nf3_file = globals_dict["selected file"][:-3]+'nf3'
    nsResult, hFile = ns_OpenFile(nf3_file,'single')
    nsResult, nf3_fileinfo = ns_GetFileInfo(hFile)
    time_difference = timedelta(seconds=nf3_fileinfo['TimeSpan'])
    rec_length = nf3_fileinfo['TimeSpan']
    task_start_datetime = datetime(year, month, day, hours, minutes, seconds)- timedelta(hours=5)     
    task_end_datetime = task_start_datetime + time_difference
    nsResult = ns_CloseFile(hFile)
    globals_dict['rec_length'] = int(time_difference.total_seconds())

def initialize_case2():
    search_pattern = os.path.join(globals_dict['selected folder'], '*.nev')
    nev_files = glob.glob(search_pattern)
    #get time for each file in the list of files

    for nev in nev_files:
        nsResult, hFile = ns_OpenFile(nev, 'single')
        nsResult, fileInfo = ns_GetFileInfo(hFile)
        nev_dict.update({nev:fileInfo})
        nsResult = ns_CloseFile(hFile)
    #checks using fileInfo
    for key in nev_dict.keys():
        seconds = nev_dict[key]['Time_Sec']
        minutes = nev_dict[key]['Time_Min']
        hours = nev_dict[key]['Time_Hour']  
        day = nev_dict[key]['Time_Day']
        month = nev_dict[key]['Time_Month']
        year = nev_dict[key]['Time_Year']
        nf3_file = key[:-3]+'nf3'
        nsResult, hFile = ns_OpenFile(nf3_file,'single')
        nsResult, nf3_fileinfo = ns_GetFileInfo(hFile)
        time_difference = timedelta(seconds=nf3_fileinfo['TimeSpan'])
        print(time_difference)
        task_start_datetime = datetime(year, month, day, hours, minutes, seconds)  - timedelta(hours=5)    
        task_end_datetime = task_start_datetime + time_difference
        nev_dict.update({key:[task_start_datetime,task_end_datetime]})
        nsResult = ns_CloseFile(hFile)
    print(task_start_datetime)
    #create datetimes from inputed mins and event time

    string_format = "%H:%M:%S"
    event_time = datetime.strptime(globals_dict['t_event'], string_format).time()
    event_start_time_difference = timedelta(seconds=int(globals_dict['t_before_event'])*60)
    event_end_time_difference = timedelta(seconds=int(globals_dict['t_after_event'])*60)
    event_datetime = datetime.combine(globals_dict["selected date"],event_time)
    event_start_datetime = event_datetime - event_start_time_difference
    event_end_datetime = event_datetime + event_end_time_difference
    event_time_difference =event_end_datetime - event_start_datetime
    globals_dict['rec_length'] = int(event_time_difference.total_seconds())
    # logic for epoching data
    flag = False
    key_list = list(nev_dict.keys())
    nf3_files = []
    nev_files = []
    for key in key_list:
        if nev_dict[key][0] < event_datetime < nev_dict[key][1]:
            nf3_files.append(key[:-3]+'nf3')
            nev_files.append(key)
            flag = True
            if event_end_datetime > nev_dict[key][1] and event_end_datetime < nev_dict[key_list[key_list.index(key)+1]][1]:
                nev_files.append(key_list[key_list.index(key)+1])
                nf3_files.append(key_list[key_list.index(key)+1][:-3]+'nf3')
            if event_start_datetime < nev_dict[key][0] and event_start_datetime > nev_dict[key_list[key_list.index(key)-1]][0]:
                nev_files.append(key_list[key_list.index(key)-1])
                nf3_files.append(key_list[key_list.index(key)-1][:-3]+'nf3')
            if len(key_list)>2:
                if (event_end_datetime > nev_dict[key_list[key_list.index(key)+1]][1] or event_start_datetime < nev_dict[key_list[key_list.index(key)-1]][0]):
                    print("epoch is too large for the event type")
                    exit()
        else:
            continue
    if flag == True:
        print("The file for the event is {}".format(nf3_files))
    elif flag == False:
        print("The file containing this event could not be found!")
    globals_dict["nf3_files"] = nf3_files
    globals_dict['nev_files'] = nev_files
    datetime_dict.update({"event_start_datetime":event_start_datetime,"event_end_datetime":event_end_datetime,"event_datetime":event_datetime})

def get_numeric_suffix(item):
    start_index = item.find('run-') + 4  # Index after "run-"
    end_index = start_index + 2  # Two characters after "run-"
    return int(item[start_index:end_index])

def get_times():
    #t_start is the amount of time from the begining of the recording to the start of the event. t_end is the amount of time from the begining of the recording to the end of the event.
    #rec_length is the amount of time between the absolute start and end of an event.
    if globals_dict['nev_files'] != None:    
        if len(globals_dict['nev_files']) > 1:
            datetime_list = []
            for key in nev_dict.keys():
                datetime_list.append(nev_dict[key])
            globals_dict['t_start_1']= int((datetime_dict['event_start_datetime'] - datetime_list[0][0]).total_seconds())
            globals_dict['t_start_2'] = 0
            globals_dict['t_end_1'] = int((globals_dict['first_rec_length']))
            globals_dict['t_end_2'] = int((datetime_dict['event_end_datetime']-datetime_list[1][0]).total_seconds())
            globals_dict['rec_length_1'] = globals_dict['first_rec_length']-globals_dict['t_start_1']
            globals_dict['rec_length_2'] = globals_dict['t_end_2']
        elif len(globals_dict['nev_files']) ==1:
            datetime_list = nev_dict[globals_dict['nev_files'][0]]
            print(datetime_list)
            globals_dict['t_start'] = int((datetime_dict['event_start_datetime'] - datetime_list[0]).total_seconds())
            globals_dict['t_end'] = int((datetime_dict['event_end_datetime'] - datetime_list[0]).total_seconds())
            globals_dict['rec_length'] = globals_dict['t_end'] - globals_dict['t_start']
    elif globals_dict['selected file'] != None:
        globals_dict['rec_length'] = globals_dict['rec_length']
        globals_dict['t_start'] = 0
        globals_dict['t_end'] = globals_dict['rec_length']

def get_NC3_folder_path():
    if globals_dict['rec_length_2'] != None:
        folder_pathes = [filedialog.askdirectory(title="select the first run folder that contains .NC3's"),filedialog.askdirectory(title="select the second run folder that contains .NC3's")]
        globals_dict['NC3_folder_pathes'] = folder_pathes
    else:
        folder_path = filedialog.askdirectory(title="select the folder that contains .NC3's")
        globals_dict['NC3_folder_path'] = folder_path

def parse_NC3():
    if globals_dict['NC3_folder_pathes'] != None:
        k = 0
        rec_length_list = [globals_dict['rec_length_1'],globals_dict['rec_length_2']]
        tmin_list = [globals_dict['t_start_1'],globals_dict['t_start_2']]
        for path in globals_dict['NC3_folder_pathes']:
            mat_contents = loadmat(path)
            # Access the struct in the loaded data
            mat_struct = mat_contents['NSx']
            # Access specific fields within the struct
            conversion = mat_struct['conversion']
            dc_offset = mat_struct['dc']
            is_micro = mat_struct['is_micro']
            folder_path = globals_dict['NC3_folder_path']
            nc3_files = []
            # Use glob to find files with the ".NC3" extension
            search_pattern = os.path.join(folder_path, '*.NC3')
            nc3_files = glob.glob(search_pattern)
            nc3_files = sorted(nc3_files, key=lambda x: os.path.basename(x))
            keys = []
            i = -1
            for file_path in nc3_files:
                i = i + 1
                j = 0
                rec_length = rec_length_list[k]
                tmin = 10+tmin_list[k]
                if is_micro[0][j][0][0] == 1:
                    sample_rate = 30000
                    globals_dict['sample_rate'] = 30000
                else:
                    sample_rate = 2000
                    globals_dict['sample_rate'] = 2000
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
                k = k+1
    else:
        mat_contents = loadmat(globals_dict['Nsx_filepath'])
        # Access the struct in the loaded data
        mat_struct = mat_contents['NSx']
        # Access specific fields within the struct
        conversion = mat_struct['conversion']
        dc_offset = mat_struct['dc']
        is_micro = mat_struct['is_micro']
        folder_path = globals_dict['NC3_folder_path']
        nc3_files = []
        # Use glob to find files with the ".NC3" extension
        search_pattern = os.path.join(folder_path, '*.NC3')
        nc3_files = glob.glob(search_pattern)
        nc3_files = sorted(nc3_files, key=lambda x: os.path.basename(x))
        keys = []
        i = -1
        for file_path in nc3_files:
            i = i + 1
            j = 0
            rec_length = globals_dict['rec_length']
            tmin = 10+globals_dict['t_start']
            if is_micro[0][j][0][0] == 1:
                sample_rate = 30000
                globals_dict['sample_rate'] = 30000
            else:
                sample_rate = 2000
                globals_dict['sample_rate'] = 2000
            fileName = os.path.basename(file_path)
            min_record = math.floor(sample_rate * tmin)
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

def get_brain_surface():
    file_path = filedialog.askopenfilename(title="select the surfaces.mat file in Registered Dicom 10 (Meg) folder", filetypes=[("MAT files","*.mat")])
    globals_dict['brain_surface_path'] = file_path

def load_brain_surface():
    brain_surface_struct = loadmat(
        globals_dict['brain_surface_path'])
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
    globals_dict['simplified_vertices'] = np.asarray(simplified_mesh.vertices)
    globals_dict['simplified_faces'] = np.asarray(simplified_mesh.triangles)
    globals_dict['simplified_triangles'] = [globals_dict['simplified_vertices'][triangle] for triangle in globals_dict['simplified_faces']]

def get_electrode_path():
    file_path = filedialog.askopenfilename(title="select the electrodes.mat file in Registered Dicom 10 (Meg) folder", filetypes=[("MAT files","*.mat")])
    globals_dict['electrode_path'] = file_path

def load_electrodes():
    with h5py.File(globals_dict['electrode_path'], 'r') as mat_file:
        # List all the keys (group names) in the HDF5 structure
        keys = list(mat_file.keys())
        # Access a specific dataset within the file
        dataset = mat_file['ElecXYZRaw']
        # Read the dataset into a NumPy array
        data = dataset[()]
    # set varaibles
    globals_dict['elec_x_center'] = data[0]
    globals_dict['elec_y_center'] = data[1]
    globals_dict['elec_z_center'] = data[2]
    # Normalize Sample data
    for key in power_dict.keys():
        norm = Normalize(vmin=0, vmax=max(power_dict[key]))
        power_dict[key] = norm(power_dict[key])

def bundle_keys(keys, bundle_dict):
    for key in keys:
        bundle_name = str(key)[:2]
        if bundle_name in bundle_dict:
            bundle_dict[bundle_name].append(key)
        else:
            bundle_dict.update({bundle_name: [key]})
    return bundle_dict
def map_electrodes():
    f = h5py.File(
        globals_dict['electrode_path'],
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
    for i in range(len(strs)):
        electrode_dict.update(
            {strs[i]: [globals_dict['elec_x_center'][i], globals_dict['elec_y_center'][i], globals_dict['elec_z_center'][i]]})
        
def move_selected_entry():
    selected_index = globals_dict['listbox'].curselection()
    if selected_index:
        selected_value = globals_dict['listbox'].get(selected_index)
        globals_dict['listbox'].delete(selected_index)
        globals_dict['listbox_right'].insert(tk.END, selected_value)
        globals_dict['selected_channels'].append(selected_value)

def select_channels():
    # Create the main window
    window = tk.Tk()
    window.title("Entry Mover")

    # Create a left scrollable box
    listbox_frame_left = tk.Frame(window)
    listbox_frame_left.pack(side=tk.LEFT, padx=10, pady=10)

    listbox_scroll_left = tk.Scrollbar(listbox_frame_left, orient=tk.VERTICAL)
    globals_dict['listbox'] = tk.Listbox(listbox_frame_left, selectmode=tk.SINGLE, yscrollcommand=listbox_scroll_left.set)

    listbox_scroll_left.config(command=globals_dict['listbox'].yview)
    listbox_scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
    globals_dict['listbox'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Populate the left listbox with sample entries
    for key in electrode_dict.keys():
        globals_dict['listbox'].insert(tk.END, key)

    # Create a button to move selected entry to the right
    move_button = tk.Button(window, text="Move >>", command=move_selected_entry)
    move_button.pack(pady=10)

    # Create a right scrollable box
    listbox_frame_right = tk.Frame(window)
    listbox_frame_right.pack(side=tk.LEFT, padx=10, pady=10)

    listbox_scroll_right = tk.Scrollbar(listbox_frame_right, orient=tk.VERTICAL)
    globals_dict['listbox_right'] = tk.Listbox(listbox_frame_right, selectmode=tk.SINGLE, yscrollcommand=listbox_scroll_right.set)

    listbox_scroll_right.config(command=globals_dict['listbox_right'].yview)
    listbox_scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
    globals_dict['listbox_right'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    
    # Run the GUI
    window.mainloop()
    
def toggle_LH():
    if var_LH.get():
        label_LH.config(text="LH is ON")
        globals_dict['toggle_LH'] = True
    else:
        label_LH.config(text="LH is OFF")
        globals_dict['toggle_LH'] = False

def toggle_RH():
    if var_RH.get():
        label_RH.config(text="RH is ON")
        globals_dict['toggle_RH'] = True
    else:
        label_RH.config(text="RH is OFF")
        globals_dict['toggle_RH'] = False

#define switch dict
ui_switch_dict = {
    'case1': ui_case1,
    'case2': ui_case2
}
#make window
window = tk.Tk()
window.title("Select file or time")
enter_file_button = tk.Button(window, text="Enter File", command=get_selected_file)
enter_file_button.pack(pady=20)
enter_time_button = tk.Button(window, text="Enter Time", command=get_enter_time)
enter_time_button.pack(pady=20)
window.mainloop()
try:
    ui_switch_dict[globals_dict["selected case"]]()
except KeyError:
    default()
# checks if time of event is empty
initialize_switch_dict = {
    'case1': initialize_case1,
    'case2': initialize_case2
}
if globals_dict['t_event'] ==None:
    initialize_switch_dict['case1']()
else:
    initialize_switch_dict['case2']()
if globals_dict['nf3_files'] != None:
    if len(globals_dict['nf3_files']) > 1:
        globals_dict['nev_files'] = sorted(globals_dict['nev_files'], key=get_numeric_suffix)
        get_rec_legnth(globals_dict['nf3_files'])
#get times
get_times()
#gets Nsx.mat file. will be changed to methods involving the python parser so .mat file is not required
get_Nsx()
#gets run folder with NC3
get_NC3_folder_path()
#Parses NC3 from binary to usable data
parse_NC3()
#get brain surface
get_brain_surface()
load_brain_surface()
#Channel selection Menu
root = tk.Tk()
root.title("Toggle LH and RH")

# Create a control variable (IntVar) to store the state of the toggle button
var_LH = tk.IntVar()
var_RH = tk.IntVar()

# Create a Checkbutton with the control variable and a command to call the toggle function
toggle_button_LH = tk.Checkbutton(root, text="Toggle", variable=var_LH, command=toggle_LH)
toggle_button_LH.pack(pady=10)

toggle_button_RH = tk.Checkbutton(root, text="Toggle", variable=var_RH, command=toggle_RH)
toggle_button_RH.pack(pady=10)

# Create a label to display the current state of the toggle
label_LH = tk.Label(root, text="LH is OFF")
label_LH.pack(pady=10)

label_RH = tk.Label(root, text="RH is OFF")
label_RH.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()


idx_start = globals_dict['t_start']*globals_dict['sample_rate']
# electrodes
# load
get_electrode_path()
load_electrodes()
# sort samples into bundels
bundle_keys(power_dict.keys(), bundle_dict)

map_electrodes()
if globals_dict['toggle_LH'] == False:
    #remove polygons that contain negative x values and remove LH entries
    globals_dict['simplified_triangles'] = [polygon for polygon in globals_dict['simplified_triangles'] if all(x >= 0 for x, _, _ in polygon)]
    electrode_dict = {key: value for key, value in electrode_dict.items() if 'L' not in key and 'l' not in key}

if globals_dict['toggle_RH'] == False:
     #remove polygons that contain positive x values and remove RH entries
    globals_dict['simplified_triangles'] = [polygon for polygon in globals_dict['simplified_triangles'] if all(x <= 0 for x, _, _ in polygon)]
    electrode_dict = {key: value for key, value in electrode_dict.items() if 'R' not in key and 'r' not in key}
select_channels()


fig = plt.figure(layout="constrained")

gs = GridSpec(int(len(bundle_dict.keys()) / 2), 4, figure=fig)
axes_dict = {}
ax1 = fig.add_subplot(gs[:, :-2], projection='3d', picker = True)
axes_dict.update({"ax1": ax1})

wireframe = Poly3DCollection(
    globals_dict['simplified_triangles'],
    facecolors='b',
    edgecolor='none',
    alpha=.1)
ax1.add_collection3d(wireframe)


# make 2D Bundles plots
i = 0
vertical_lines = []
for channel in globals_dict['selected_channels']:
    if i < len(globals_dict['selected_channels']) / 2:
        ax_i = fig.add_subplot(gs[i, 2])
    else:
        ax_i = fig.add_subplot(gs[i - int(len(globals_dict['selected_channels']) / 2), 3])
    axes_dict.update({"ax%s" % (str(channel)): ax_i})
    x = [i / globals_dict['sample_rate'] + globals_dict['t_start'] for i in range(len(raw_dict[channel]))]
    y = power_dict[channel]
    norm = Normalize(vmin=0,vmax=max(y))
    norm(y)
    data_array = np.vstack((x, y))
    ax_i.imshow(data_array[1:2, :],cmap='viridis',aspect='auto',interpolation='none',extent=[np.min(x), np.max(x), np.min(y), np.max(y)])
    scalar_mappable = cm.ScalarMappable(norm=norm, cmap='viridis')
    scalar_mappable.set_array([])
    fig.colorbar(scalar_mappable,ax=ax_i)
    ax_i.set_title(str(channel))
    ax_i.set_xlabel("time")
    vertical_lines.append(ax_i.axvline(x= globals_dict['t_start'], color='red', linestyle='--'))
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
    idx_step = round(1 / ((1 / globals_dict['sample_rate']) / (1 / fps)), 2)
    t_step = idx_step/globals_dict['sample_rate']
    print(idx_step)
    idx = int(idx_step * (frame + 1))
    print(idx)
    print(idx_start)
    t = t_step*(frame+1) + globals_dict['t_start']#might need to add start_idx to get correct t
    print(t)
    j = 0
    for i in electrode_dict.keys():
        if 'm' in i:
            print("no micro")
        elif idx>len(colormap_dict[i]):
            break
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

#fig.canvas.mpl_connect('pick event', onpick)
ani = FuncAnimation(fig, update, frames=((globals_dict['t_end']-globals_dict['t_start'])*fps)-1, interval=1000 / 30)
output_file = 'frames/frames.gif'
#ani.save(output_file, writer='pillow')
#ani.to_jshtml([fps, embed_frames, default_mode]) #then open as a html file to have a viewer
# Set the resolution for saving
dpi = 100  # Adjust as needed
fig.set_size_inches(1920 / dpi, 1080 / dpi)
ani.to_html5_video()
with open("3DAnimation.html", "w") as f:
    print(ani.to_html5_video(), file=f)


plt.show()
