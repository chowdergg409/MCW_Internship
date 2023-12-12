import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from matplotlib import pyplot
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from pandas import DataFrame
from datetime import datetime, timedelta
from collections import Counter
from matplotlib.widgets import Button, RadioButtons, CheckButtons, Slider, Cursor
import PySimpleGUI as sg
from os import listdir
from os.path import isfile, join
import tkinter as tk
from tkinter import filedialog
import os
from pathlib import Path
import sys ; sys.path.append('/home/hauderc/Documents/GitHub/codes_emu/neuroshare/python')
from ns_get_analog_data_block import ns_GetAnalogDataBlock
from ns_get_analog_data import ns_GetAnalogData
from ns_close_file import ns_CloseFile
from ns_get_analog_info import ns_GetAnalogInfo
from ns_get_entity_info import ns_GetEntityInfo
from ns_open_file import ns_OpenFile
from ns_get_file_info import ns_GetFileInfo
#callback 
class Index:
    def __init__(self,shared):
        self.shared = shared
    def table(self,event):
        event, values = sg.Window('Choose an option', [[sg.Text('Select one->'), sg.Listbox(names, size=(20, 10), key='LB')],
        [sg.Button('Ok'), sg.Button('Cancel')]]).read(close=True)
        self.shared['name_selection'] = values["LB"][0]
        if event == 'Ok':
            event, values = sg.Window('Choose the function',[[sg.Text('Select one->'),sg.Listbox(plot_functions,size=(20,10), key='LB')],[sg.Button('Ok'),sg.Button('Cancel')]]).read(close=True)
            self.shared['function_selection'] = values["LB"][0]
        else:
            sg.popup_cancel('User aborted')
#shared global dictionary
shared = {}
#random date generator


filePaths = []

def get_directory():
    directory = filedialog.askdirectory()
    return directory

names = [] 
def get_filepathes(directory):
    for item_path in Path(directory).rglob('*'):
        # Print the current item (file or subdirectory)
        filePaths.append(item_path)
    names = filePaths
    return filePaths, names

nev_files = []
def get_nev_files(filePaths):
    nev_files = [file_path for file_path in map(Path, filePaths) if file_path.suffix == '.nev']
    return nev_files

nf3_files = []
def get_nf3_files(filePaths):
    nf3_files = [file_path for file_path in map(Path, filePaths) if file_path.suffix == '.nf3']
    return nf3_files

start_datetimes = []
def get_start_datetime(nev_files, nf3_files):
    good_nev_files = []
    good_nf3_files = []
    print(len(nev_files))
    for i in range(len(nev_files)):
        try:
            print(nev_files[i])
            nsResult, hFile = ns_OpenFile(nev_files[i], 'single')
            nsResult, fileInfo = ns_GetFileInfo(hFile)
            nsResult = ns_CloseFile(hFile)
            seconds = fileInfo['Time_Sec']
            minutes = fileInfo['Time_Min']
            hours = fileInfo['Time_Hour']
            day = fileInfo['Time_Day']
            month = fileInfo['Time_Month']
            year = fileInfo['Time_Year']
            start_datetime = datetime(year, month, day, hours, minutes, seconds) - timedelta(hours=5)
            start_datetimes.append(start_datetime)
            good_nev_files.append(nev_files[i])
            good_nf3_files.append(nf3_files[i])
        except:
            print('bad file')
    nev_files = good_nev_files
    nf3_files = good_nf3_files
    names = good_nev_files
    return start_datetimes, nev_files, nf3_files, names

end_datetimes = []
def get_end_datetime(nf3_files, start_datetimes):
    for i in range(len(nf3_files)):
        nsResult, hFile = ns_OpenFile(nf3_files[i],'single')
        nsResult, fileInfo = ns_GetFileInfo(hFile)
        nsResult = ns_CloseFile(hFile)
        time_span = timedelta(seconds=fileInfo['TimeSpan'])
        end_datetime = start_datetimes[i] + time_span
        end_datetimes.append(end_datetime)
    return end_datetimes

tasks = []
colors = []
def get_task_and_colors(names):
    for name in names:
        print(name)
        s = str(name)
        
        if 'gaps'in s:
            tasks.append("Gaps")
            colors.append('y')
        elif 'RSVPdynamic' in s:
            tasks.append("RSVPdynamic")
            colors.append('b')
        elif 'Recall' in s:
            tasks.append("Recall")
            colors.append('m')
        elif 'Picture-Naming'in s:
            tasks.append("Picture Naming")
            colors.append('k')
        elif 'DefinitionNaming'in s:
            tasks.append("DefinitionNaming")
            colors.append('g')
        else: 
            tasks.append("NONE")
            colors.append('w')

    return tasks, colors

directory = get_directory()
filepaths = get_filepathes(directory)
nev_files = get_nev_files(filePaths)
nf3_files =get_nf3_files(filePaths)
start_datetimes, nev_files, nf3_files, names= get_start_datetime(nev_files, nf3_files)
end_datetimes =get_end_datetime(nf3_files,start_datetimes)
tasks, colors = get_task_and_colors(names)
#Timeline df
#clinical df
clinical_d = {'ClinicalEvent':[],'Start':[],'End':[],'Duration':[]}
clinical_df = pd.DataFrame(data=clinical_d)

print(len(nev_files))
print(len(nf3_files))
print(len(names))
print(len(start_datetimes))
print(len(end_datetimes))
print(len(tasks))
print(len(colors))

timeline_d = {'nev_files':nev_files,'nf3_files':nf3_files,'Name':names,'Start':start_datetimes, 'End':end_datetimes,'Task':tasks,'Color':colors}
timeline_df = pd.DataFrame(data=timeline_d)
print(timeline_df)
#plotting
levels = np.tile([-5, 5, -3, 3, -1, 1],
                 int(np.ceil(len(start_datetimes)/6)))[:len(start_datetimes)]#levels for stems
fig, ax = plt.subplots(figsize=(8.8, 4), layout="constrained")#initialize axis
ax.set(title="Patient xxx Timeline")#title
ax.vlines(start_datetimes, 0, levels, colors)#start colors
ax.vlines(end_datetimes, 0, levels, colors)   # The vertical stems.
ax.plot(start_datetimes, np.zeros_like(start_datetimes), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it for start dates.
ax.plot(end_datetimes, np.zeros_like(end_datetimes), "-o", color="k", markerfacecolor="w")#baseline and markers on it for end dates.
for d, l, r in zip(start_datetimes[::10], levels[::10], names[::10]):#every 10th index is labeled and aligns with the start date.
    ax.annotate(r, xy=(d, l),
                xytext=(-3, np.sign(l)*3), textcoords="offset points",
                horizontalalignment="right",
                verticalalignment="bottom" if l > 0 else "top")
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(24),interval=6))#every 6 hours is shown on axis
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y %H:%M:%S"))#format of date and time
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")#ticks on axis
ax.yaxis.set_visible(False)#no y axis
ax.spines[["left", "top", "right"]].set_visible(False)
ax.margins(y=0.1)
axes = plt.axes([0.81, 0.000001, 0.1, 0.075])#axis location
#button
#legend
yellow_patch = mpatches.Patch(color='yellow', label='Task Gaps')
blue_patch = mpatches.Patch(color='blue', label='RSVP dynamic')
magenta_patch = mpatches.Patch(color='magenta', label='Recall')
black_patch = mpatches.Patch(color='black', label='Picture Naming')
green_patch = mpatches.Patch(color='green', label='Definition Naming')
ax.legend(handles=[yellow_patch,blue_patch,magenta_patch,black_patch,green_patch])
#callback for button on graph
callback= Index(shared)
table_button = Button(axes, 'table',color="yellow")
table_button.on_clicked(callback.table)
plt.show()
#get share variables from selections of the callback
file = shared.get("name_selection")
plot_function = shared.get("function_selection")