import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import sys
import os
import math

# Load the CSV data
file_path = 'grid_log.csv'
file_data = []
with open(file_path, 'r') as fin:
    file_data = fin.read().splitlines(True)

delim = file_data[0].split("=")[-1]

with open('temp_log.csv', 'w') as fout:
    fout.writelines(file_data[1:])

data = pd.read_csv('temp_log.csv', sep=";")
os.remove("temp_log.csv")

ff_data = data.copy(deep=True)

#Set axis time
def seconds_to_hms_ms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Split seconds into whole seconds and milliseconds
    seconds_whole, milliseconds = divmod(seconds, 1)
    # Format milliseconds to desired precision, e.g., 3 digits
    milliseconds = int(milliseconds * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds_whole):02d}.{milliseconds:03d}"


# Progress bar animation
def progress_bar(current, total, bar_length=50):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current == total else '\r'
    sys.stdout.write(f'Progress: [{arrow}{padding}] {int(fraction*100)}%{ending}')
    sys.stdout.flush()

# Grid dimensions and origin
grid_size = (10, 10, 3)
origin = (0, 0)

# Initialize the grid
grid = np.zeros(grid_size)

first_frame = {'loc': [], 'data': []}

for [time, model_id, loc, port, _data] in zip(ff_data['time'], ff_data['model_id'], ff_data['model_name'], ff_data['port_name'], ff_data['data']):
    nan_flag = False
    try:
        nan_flag = math.isnan(port)
    except:
        nan_flag = False

    if(time == 0 and nan_flag):
        if(loc not in first_frame['loc']):
            first_frame['loc'].append(loc)
            first_frame['data'].append(_data)

for [loc, _data] in zip(first_frame['loc'], first_frame['data']):
    x, y = map(int, loc.strip('()').split(','))
    state = int(_data.strip('<>')[0])

    color_val = (0, 0, 1)
    if state == 1:
        color_val = (1, 0, 0)
    elif state == 0:
        color_val = (0, 0, 0)

    grid[y - origin[1], x - origin[0]] = color_val  # Update grid with the color value

fig, ax = plt.subplots()
mat = ax.matshow(grid, cmap='gray')  # Use a grayscale colormap or any other suitable colormap

# Draw grid lines
ax.set_xticks(np.arange(-.5, grid.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-.5, grid.shape[0], 1), minor=True)
# ax.grid(which="both", color="w", linestyle='-', linewidth=1)
ax.tick_params(which="minor", size=0)

# Optional: Remove ticks and labels
ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Time 00:00:00:000")

# Extract the unique times for animation frames
times = data['time'].unique()

# Update function for animation
def update(frame_num):
    frame_data = data[(data['time'] + 1) == times[frame_num]]
    for _, row in frame_data.iterrows():
        x, y = map(int, row['model_name'].strip('()').split(','))
        state = int(row['data'].strip('<>')[0])

        color_val = (0, 0, 1)
        if state == 1:
            color_val = (1, 0, 0)
        elif state == 0:
            color_val = (0, 0, 0)

        grid[y - origin[1], x - origin[0]] = color_val  # Update grid with the color value

    mat.set_data(grid)  # Update the image with the new grid
    ax.set_title(f"Time {seconds_to_hms_ms(times[frame_num])}")
    progress_bar(frame_num + 1, len(times))
    
    return [mat]

# Remove rows where 'port_name' is populated
data = data[data['port_name'].isnull()]

print('Initializing animation')
# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(times), interval=500)

print('Saving the animation')
# Save the animation as a video file
ani.save('Gate_animation.mp4', writer='ffmpeg', dpi=150)
