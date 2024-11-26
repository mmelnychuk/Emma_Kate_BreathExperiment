# MEDITATION SELF ALERT TASK

import tkinter as tk
import time
import csv
import json
import subprocess
import atexit
import os


# import os
#
# print("Current working directory:", os.getcwd())

# get vars from json file
# Read from file
try:
    with open('task_data.json', 'r') as f:
        task_data = json.load(f)
        if task_data:
            participant_id = task_data["participant_id"]
            total_time = task_data["task_2_time"]
            print(task_data)
except:
    participant_id = "participant"
    total_time = 10  # 10 seconds for testing
print(total_time, participant_id)
filename = f'subject_data/{participant_id}/MW.csv'
sniff_filename = f'subject_data/{participant_id}/MW_sniff.csv'
os.makedirs(os.path.dirname(filename), exist_ok=True)

# Initialize the CSV file with the header
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['UnixTime'])
    #Note: *** UnixTime not sync'd between devices possibly ***


def write_time_to_file(unix_time):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([unix_time])


def on_key(event):
    unix_time = (time.time())
    write_time_to_file(unix_time)
    # print(f"Key pressed: {event.keysym}, Unix time: {unix_time}")
    print(f"Your mind wandered at Unix time: {unix_time}")
    # Update the label with the new message
    label.config(text=f"key pressed.", font=("Helvetica", 48), bg="white", fg="red")
    # Clear the message after n seconds (n000 milliseconds)
    root.after(2000, clear_message)
def on_click(event):
    unix_time = (time.time())
    write_time_to_file(unix_time)
    print(f"Your mind wandered at Unix time: {unix_time}")
    # Update the label with the new message
    label.config(text=f"Your mind wandered at Unix time: {unix_time}")
    # Clear the message after n seconds (n000 milliseconds)
    root.after(2000, clear_message)

def clear_message():
    label.config(text="Press the spacebar \n if your mind wanders from the breath.", font=("Helvetica", 64), bg="white", fg="black")

def cancel():
    root.destroy()

def say_goodbye():
    process.terminate()
    global label
    root.unbind('<Key>')
    label.config(text="Task is Finished. \n Please let the Experimenter know.")
    # Schedule the window to close 2 seconds after showing the goodbye message
    root.after(2000, root.destroy)


def start_experiment():
    # Create the main window
    instruction_window.destroy()
    global root
    global label
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='white')
    root.after(total_time*1000, say_goodbye)  # use `total_time` env var for final ver

    # Create a label with minimal instructions (intro and reminder after mw if eyes open)
    label = tk.Label(root, text="Press the spacebar \n if your mind wanders from the breath.", font=("Helvetica", 64), bg="white", fg="black")
    label.pack(pady=20, expand=True)

    # Bind key press event to the on_key function
    root.bind('<Key>', on_key)

    # Bind mouse click events to the on_click function
    # root.bind('<Button-1>', on_click)  # Left mouse button
    # root.bind('<Button-2>', on_click)  # Middle mouse button
    # root.bind('<Button-3>', on_click)  # Right mouse button

    # Create a button to cancel and close the application
    cancel_button = tk.Button(root, text="End Session", font=("Helvetica", 24), command=cancel)
    cancel_button.pack(pady=20)

    # start sniffing
    global process
    process = subprocess.Popen(['python3', 'getSniffs.py', sniff_filename])

    # Ensure subprocesses are terminated if and when the main script exits
    def terminate_subprocess():
        process.terminate()

    atexit.register(terminate_subprocess)  # this will kill getSniffs and 'signal will close serial port connection

    # Start the Tkinter event loop
    root.mainloop()

global instruction_window
instruction_window = tk.Tk()
instruction_window.attributes('-fullscreen', True)
instruction_window.configure(background='white')
instruction_window.title("Instructions")

# Add instructions label
instructions = (
    "BREATH FOCUS TASK\n\n\n"
    "Close your eyes and focus on your breathing.\n\n"
    "Focus on the sensations of your breathing\n\n"
    "(at your nostrils or your abdomen, for example.)\n\n"
    "Press the spacebar as soon as you notice your mind has wandered\n\n"
    "from your breath and then begin to focus again on your breathing. \n\n"
    "Take a minute to feel your breath before the task begins.\n\n"
    "Press 'Start' when you are ready.\n\n"
)

label = tk.Label(instruction_window, text=instructions, font=("Helvetica", 36), bg="white", fg="black", justify="center")
label.pack(pady=20)

# Add a button to start the experiment
start_button = tk.Button(instruction_window, text="Start", command=start_experiment, font=("Helvetica", 24), bg="gray")
start_button.pack(pady=20)

# Start the instruction window loop
instruction_window.mainloop()
