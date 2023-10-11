import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from matplotlib import pyplot
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from pandas import DataFrame
from datetime import datetime
from collections import Counter
from matplotlib.widgets import Button, RadioButtons, CheckButtons, Slider, Cursor
import PySimpleGUI as sg
from os import listdir
from os.path import isfile, join

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
def random_date_generator(start_date, range_in_days, range_in_seconds):
    days_to_add = np.arange(0, range_in_days)
    random_date = np.datetime64(start_date) + np.random.choice(days_to_add)
    seconds_to_add = np.arange(0,range_in_seconds )
    random_time = np.datetime64(random_date) + np.random.choice(seconds_to_add)
    return random_time
#Timeline df
timeline_d = {'FilePath':[],'Name':[],'Start':[], 'End':[],'Task':[],'Color':[]}
timeline_df = pd.DataFrame(data=timeline_d)
#clinical df
clinical_d = {'ClinicalEvent':[],'Start':[],'End':[],'Duration':[]}
clinical_df = pd.DataFrame(data=clinical_d)
#initialize random date arrays
x = np.zeros(shape =(60),dtype='datetime64[s]')#use length
y = np.zeros(shape = (60),dtype='datetime64[s]')
for i in range(60): #use length
    x[i] =random_date_generator('2023-09-20T00:00:00',5,86400)#
for i in range(60): #use length
    y[i] = random_date_generator('2023-09-20T00:00:00',5,86400)#
#initialize names array
names = np.array([]) 
#start times
x.sort()
starts = x
starts_str = np.array(np.datetime_as_string(x))
starts_d = {'Start':starts_str}
starts_df = pd.DataFrame(starts_d)
timeline_df = pd.concat([timeline_df,starts_df],ignore_index=False, sort=False)
#end times
y.sort()
ends = y
ends_str = np.array(np.datetime_as_string(y))
ends_d = {'End':ends_str}
ends_df = pd.DataFrame(data=ends_d)
timeline_df.set_index('End')
ends_df.set_index('End')
timeline_df.update(ends_df) 
#functions for plotting
plot_functions = np.array(["Scatter", "Power Spectrum", "Other"])
#name generator will be replaced with get name function
for j in range(60):#use length
    names = np.append(names,["random event"+str(j)])#something like this names = np.append(names,[name])
names_d = {'Name':names}
names_df = pd.DataFrame(data=names_d)
timeline_df.set_index('Name')
names_df.set_index('Name')
timeline_df.update(names_df)
#assign tasks and colors
tasks = []
colors = []
for i in range(len(timeline_df["Name"])):
    print(timeline_df["Name"][i])
    match timeline_df["Name"][i]:
        case str(s) if '0'  in s:#if 'gaps'in s
            tasks.append("Gaps")
            colors.append('y')
        case str(s) if '2' in s:#if 'RSVPdynamic' in s
            tasks.append("RSVPdynamic")
            colors.append('b')
        case str(s) if '3' in s:# if 'Recall' in s
            tasks.append("Recall")
            colors.append('m')
        case str(s) if '4' in s:# if 'Picture Naming'in s
            tasks.append("Picture Naming")
            colors.append('k')
        case str(s) if '5' or '6' or '7' or '8' or '9'in s:# if 'DefinitionNaming'in s
            tasks.append("DefinitionNaming")
            colors.append('g')
#add colors to dataframe
colors_d = {'Color':colors}
colors_df = pd.DataFrame(data=colors_d)
timeline_df.set_index('Color')
colors_df.set_index('Color')
timeline_df.update(colors_df) 
#add tasks to data frame
tasks_d = {'Task':tasks}
tasks_df = pd.DataFrame(data=tasks_d)
timeline_df.set_index('Task')
tasks_df.set_index('Task')
timeline_df.update(tasks_df) 
print(timeline_df)
#plotting

levels = np.tile([-5, 5, -3, 3, -1, 1],
                 int(np.ceil(len(starts)/6)))[:len(starts)]#levels for stems
fig, ax = plt.subplots(figsize=(8.8, 4), layout="constrained")#initialize axis
ax.set(title="Patient xxx Timeline")#title
ax.vlines(starts, 0, levels, colors)#start colors
ax.vlines(ends, 0, levels, colors)   # The vertical stems.
ax.plot(starts, np.zeros_like(starts), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it for start dates.
ax.plot(ends, np.zeros_like(ends), "-o", color="k", markerfacecolor="w")#baseline and markers on it for end dates.
for d, l, r in zip(starts[::10], levels[::10], names[::10]):#every 10th index is labeled and aligns with the start date.
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



#new plot of channels at timestamp
fig = plt.figure()
ax = fig.subplots()
plt.subplots_adjust(left=0.3, bottom=0.25)
x1 = np.array([0, 1, 2, 3])
y1 = np.array([5, 2, 8, 6])
x2 = np.array([0, 1, 2, 3])
x3 = np.array([0, 1, 2, 3])
y3 = np.array([0, 3, 2, 19])
y2 = np.array([10, 2, 0, 12])
p1, = ax.plot(x1,y1, color="blue", marker = "o")
p2,= ax.plot(x2,y2, color="blue", marker = "o")
p3, = ax.plot(x3,y3, color="blue", marker = "o")
#line function
lines = [p1, p2, p3]
labels = ["plot1", "plot2", "plot3"]

def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    fig.canvas.draw()
 
label = [True, True, True]

 
# xposition, yposition, width and height
ax_check = plt.axes([0.9, 0.001, 0.2, 0.3])
plot_button = CheckButtons(ax_check, labels, label)
plot_button.on_clicked(func)
#cursor = Cursor(ax, useblit=True, color='red', linewidth=2)

plt.show()

