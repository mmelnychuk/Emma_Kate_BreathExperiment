# KORNHUBER TASK
# -----To produce one voluntary movement per 2-3 respiration cycles, participants were asked to press
# the button every 8–12 s. Importantly, participants were
# asked (1) not to count any numbers (e.g., seconds) to estimate the time, (2) to avoid
# making regular or rhythmic button presses to maximize the spontaneity of the
# task. Before the real recordings, participants conducted a short training session
# (∼1 min) and the experimenter gave feedback on the interval and regularity of their
# button presses, so that participants could adjust them

# task_data["participant_id"], task_data["task_1_time"] -- use for importing vars passed with exec(open...)

import tkinter as tk
import time
import csv
import json
import subprocess
import atexit
import os

# get vars from json file
# Read from file
try:
    with open(f'task_data.json', 'r') as f:
        task_data = json.load(f)
    if task_data:
        participant_id = task_data["participant_id"]
        total_time = task_data["task_1_time"]
        print(task_data)
except:
    participant_id = "participant"
    total_time = 480  # 8 minutes

# print("Current working directory:", os.getcwd())

# total task time in seconds (will be imported as env var later)
# total_time = 480
# get start time (UXT)
start_time = time.time()

# file to save results to
filename = f'subject_data/{participant_id}/KH.csv'
# Ensure the directory exists
os.makedirs(os.path.dirname(filename), exist_ok=True)
sniff_filename = f'subject_data/{participant_id}/KH_sniff.csv'

# Initialize the CSV file with the header
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['UnixTime'])
    # Note: *** UnixTime not sync'd between devices ***


def write_time_to_file(unix_time):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([unix_time])


def on_key(event):
    global label
    unix_time = (time.time())
    write_time_to_file(unix_time)
    # print("Key pressed.")
    label.config(text="Key pressed.", font=("Helvetica", 64), bg="white",
                 fg="red")
    # os.system('say "you dumb ass. not even close."')
    # os.system('afplay /System/Library/Sounds/Glass.aiff')
    # Update the label with the new message
    # label.config(text=f"Your mind wandered at Unix time: {unix_time}")
    # Clear the message after n seconds (n000 milliseconds)
    experiment_window.after(1000, clear_message)
# def on_click(event):
#     unix_time = (time.time())
#     write_time_to_file(unix_time)
#     os.system('echo -e "\a"')
#     # Update the label with the new message
#     # label.config(text=f"Your mind wandered at Unix time: {unix_time}")
#     # Clear the message after n seconds (n000 milliseconds)
#     root.after(1000, clear_message)


def on_key_practice(event):
    global label
    unix_time = (time.time())
    write_time_to_file(unix_time)
    # print("Key pressed.")
    label.config(text="Key pressed (practice).", font=("Helvetica", 64), bg="white",
                 fg="red")
    # os.system('say "you dumb ass. not even close."')
    # os.system('afplay /System/Library/Sounds/Glass.aiff')
    # Update the label with the new message
    # label.config(text=f"Your mind wandered at Unix time: {unix_time}")
    # Clear the message after n seconds (n000 milliseconds)
    experiment_window.after(1000, clear_message)
# def on_click(event):
#     unix_time = (time.time())
#     write_time_to_file(unix_time)
#     os.system('echo -e "\a"')
#     # Update the label with the new message
#     # label.config(text=f"Your mind wandered at Unix time: {unix_time}")
#     # Clear the message after n seconds (n000 milliseconds)
#     root.after(1000, clear_message)


def clear_message():
    global label
    label.config(text="Press the spacebar key \n  every 8-12 seconds.", font=("Helvetica", 64), bg="white", fg="black")


def cancel():
    experiment_window.destroy()


def say_goodbye_practice():
    global label
    experiment_window.unbind('<Key>')
    label.config(text="Task is Finished. \n Please let the Experimenter know.")
    # Schedule the window to close some seconds after showing the goodbye message
    experiment_window.after(4000, experiment_window.destroy)
    print('experiment window destroyed')


def say_goodbye():
    process.terminate()
    global label
    experiment_window.unbind('<Key>')
    label.config(text="Task is Finished. \n Please let the Experimenter know.")
    # Schedule the window to close 2 seconds after showing the goodbye message
    experiment_window.after(2000, experiment_window.destroy)


# def practice_round():
#     instruction_window.destroy()  # Close the instruction window
#     # Create the main window
#     global experiment_window
#     experiment_window = tk.Tk()
#     experiment_window.attributes('-fullscreen', True)
#     experiment_window.geometry(f"{experiment_window.winfo_screenwidth()}x{experiment_window.winfo_screenheight()}")
#     experiment_window.resizable(False, False)  # Disable window resizing
#     experiment_window.configure(background='white')
#     experiment_window.title('One Minute Practice')
#
#     experiment_window.after(10*1000, say_goodbye_practice)  # set for one minute for practice
#
#     # Create a label with minimal instructions (intro and reminder if eyes open)
#     global label
#     label = tk.Label(experiment_window, text="Press the spacebar key \n every 8-12 seconds.", font=("Helvetica", 64), bg="white", fg="black")
#     label.pack(pady=20, expand=True)
#
#     # Bind key press event to the on_key function
#     experiment_window.bind('<Key>', on_key_practice)
#
#     # Bind mouse click events to the on_click function
#     # root.bind('<Button-1>', on_click)  # Left mouse button
#     # root.bind('<Button-2>', on_click)  # Middle mouse button
#     # root.bind('<Button-3>', on_click)  # Right mouse button
#
#     # Create a button to cancel and close the application
#     cancel_button = tk.Button(experiment_window, text="End Session", font=("Helvetica", 24), command=cancel)
#     cancel_button.pack(pady=20)
#
#     # Start the Tkinter event loop
#     experiment_window.mainloop()


def start_experiment():
    instruction_window.destroy()  # Close the instruction window
    # Create the main window
    global experiment_window
    experiment_window = tk.Tk()
    experiment_window.attributes('-fullscreen', True)
    experiment_window.geometry(f"{experiment_window.winfo_screenwidth()}x{experiment_window.winfo_screenheight()}")
    experiment_window.resizable(False, False)  # Disable window resizing
    experiment_window.configure(background='white')

    experiment_window.after(total_time*1000, say_goodbye) # set for 20s -- use `total_time` env var for final ver

    # Create a label with minimal instructions (intro and reminder if eyes open)
    global label
    label = tk.Label(experiment_window, text="Press the spacebar key \n every 8-12 seconds.", font=("Helvetica", 64), bg="white", fg="black")
    label.pack(pady=20, expand=True)

    # Bind key press event to the on_key function
    experiment_window.bind('<Key>', on_key)

    # Bind mouse click events to the on_click function
    # root.bind('<Button-1>', on_click)  # Left mouse button
    # root.bind('<Button-2>', on_click)  # Middle mouse button
    # root.bind('<Button-3>', on_click)  # Right mouse button

    # Create a button to cancel and close the application
    cancel_button = tk.Button(experiment_window, text="End Session", font=("Helvetica", 24), command=cancel)
    cancel_button.pack(pady=20)

    # start sniffing
    global process
    process = subprocess.Popen(['python3', 'getSniffs.py', sniff_filename])


    # Ensure subprocesses are terminated if and when the main script exits
    def terminate_subprocess():
        process.terminate()

    atexit.register(terminate_subprocess)  # this will kill getSniffs and 'signal will close serial port connection

    # Start the Tkinter event loop
    experiment_window.mainloop()

# # Create the first instruction window (practice)
# global instruction_window
# instruction_window = tk.Tk()
# instruction_window.attributes('-fullscreen', True)
# instruction_window.configure(background='white')
# instruction_window.title("Instructions")
#
# # Add instructions label
# instructions = (
#     "TIME ESTIMATION TASK\n\n\n\n"
#     "Press the spacebar every 8-12 seconds.\n\n"
#     "Estimate the time but do not count seconds.\n\n"
#     "Avoid rhythmic responses and try to be spontaneous.\n\n"
#     "Press 'Start' to do a short practice session.\n\n"
# )
#
# label = tk.Label(instruction_window, text=instructions, font=("Helvetica", 48), bg="white", fg="black", justify="center")
# label.pack(pady=20)
#
# # Add a button to start the experiment
# start_button = tk.Button(instruction_window, text="Start", command=practice_round, font=("Helvetica", 48))
# start_button.pack(pady=20)
#
#
# # Start the instruction window loop
# instruction_window.mainloop()
#
# print('got past the practice round')

# Create the second instruction window (real task)
# global instruction_window
instruction_window = tk.Tk()
instruction_window.attributes('-fullscreen', True)
instruction_window.configure(background='white')
instruction_window.title("Instructions")

# Add instructions label
instructions = (
    "TIME ESTIMATION TASK\n\n\n\n"
    "Practice completed.\n\n"
    "Press the spacebar every 8-12 seconds.\n\n"
    "Estimate the time but do not count seconds.\n\n"
    "Avoid rhythmic responses and try to be spontaneous.\n\n"
    "Press 'Start' to proceed to the task.\n\n"
)

label = tk.Label(instruction_window, text=instructions, font=("Helvetica", 36), bg="white", fg="black", justify="center")
label.pack(pady=20)

# Add a button to start the experiment
start_button = tk.Button(instruction_window, text="Start", command=start_experiment, font=("Helvetica", 24))
start_button.pack(pady=20)

# Start the instruction window loop
instruction_window.mainloop()