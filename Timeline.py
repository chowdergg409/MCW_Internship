import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
from sklearn.datasets import make_blobs
from matplotlib import pyplot
import matplotlib.dates as mdates
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
#for i in EMU:
    #folders = os.listdir()
    #for j in folders:
        #matlabstruct = os.path(j)
        #length = len(matlabstruct) + length
#array of random dates
x = np.zeros((60),dtype='datetime64[s]')#use length
for i in range(60): #use length
    x[i] = np.array(random_date_generator('2023-09-20T00:00:00',5,86400),dtype='datetime64[s]')#
#initialize names array
names = np.array([]) 
times = x
plot_functions = np.array(["Scatter", "Power Spectrum", "Other"])
np.sort(times)
#strip time form data
#for d in x:
#    
#    times = [datetime.strptime(d, "%Y/%m/%dT%H:%M:%S") for d in x]
#get names from folders
#add names to names array
#with our data
#for i in EMU:
    #folders = os.listdir()
    #for j in folders:
        #names[i] = string(os.path(j))
for j in range(60):#use length
    names = np.append(names,["random event"+str(j)])#something like this names = np.append(names,[name])

levels = np.tile([-5, 5, -3, 3, -1, 1],
                 int(np.ceil(len(times)/6)))[:len(times)]
fig, ax = plt.subplots(figsize=(8.8, 4), layout="constrained")
ax.set(title="Patient xxx Timeline")
ax.vlines(times, 0, levels, color="tab:red")  # The vertical stems.
#ax.vlines(dictionary[all starts], 0, levels, color=dictionary[all the colors])
#ax.vline(dictionary[all ends], 0 ,levels, color-dictionary[all the colors])
#colors
#'b' as blue
#'g' as green
#
#'r' as red
#
#'c' as cyan
#
#'m' as magenta
#
#'y' as yellow
#
#'k' as black
#
#'w' as white

ax.plot(times, np.zeros_like(times), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.
for d, l, r in zip(times[::10], levels[::10], names[::10]):#every 10th index is labeled
    ax.annotate(r, xy=(d, l),
                xytext=(-3, np.sign(l)*3), textcoords="offset points",
                horizontalalignment="right",
                verticalalignment="bottom" if l > 0 else "top")
ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(24),interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y %H:%M:%S"))

plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
ax.yaxis.set_visible(False)
ax.spines[["left", "top", "right"]].set_visible(False)
ax.margins(y=0.1)
axes = plt.axes([0.81, 0.000001, 0.1, 0.075])
#button

#legend = ax.legend(Tasktype, colors, loc="upper right", title="Colors")

callback= Index(shared)
table_button = Button(axes, 'table',color="yellow")
table_button.on_clicked(callback.table)



plt.show()
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

