import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import numpy as np
total_frames = 100
# Function to update the plot for each frame
frame = 0
def update(frame):
    global current_frame
    current_frame = frame
    line.set_ydata(np.sin(x + frame / 10.0))
    return line,

def pause_animation(event):
    animation.pause()
def play_animation(event):
    animation.resume()
def rewind_animation(event):
    global current_frame
    
def forward_animation():
    global current_frame
    current_frame = min(total_frames - 1, current_frame + 1)

# Create a figure and axis
fig, ax = plt.subplots()
x = np.linspace(0, 2 * np.pi, 100)
line, = ax.plot(x, np.sin(x))

#Create buttons
button_pause = Button(plt.axes([0.1, 0.01, 0.1, 0.05]), 'Pause')
button_pause.on_clicked(pause_animation)

button_play = Button(plt.axes([0.55, 0.01, 0.1, 0.05]), 'Play')
button_play.on_clicked(play_animation)

button_rewind = Button(plt.axes([0.25, 0.01, 0.1, 0.05]), 'Rewind')
button_rewind.on_clicked(rewind_animation)

button_forward = Button(plt.axes([0.4, 0.01, 0.1, 0.05]), 'Forward')
button_forward.on_clicked(forward_animation)

# Create the animation
animation = FuncAnimation(fig, update, frames=total_frames, interval=100)

plt.show()
