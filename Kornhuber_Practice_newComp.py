# KORNHUBER TASK -- PRACTICE***

import tkinter as tk
from tkinter import ttk
import time
import csv


# print("Current working directory:", os.getcwd())

# total task time in seconds (will be imported as env var later)
total_time = 60
# get start time (UTX)
start_time = time.time()

# file to save results to
filename = '/Users/joanne/PycharmProjects/sniff/Kornhuber_data.csv'

# Initialize the CSV file with the header
# with open(filename, 'w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['UnixTime'])
    #Note: *** UnixTime not sync'd between devices ***


#def write_time_to_file(unix_time):
     # with open(filename, 'a', newline='') as file:
     #     writer = csv.writer(file)
     #     writer.writerow([unix_time])


def on_key(event):
    global label
    unix_time = (time.time())
    # write_time_to_file(unix_time)
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

def clear_message():
    global label
    label.config(text="Press the spacebar key \n  every 8-12 seconds.", font=("Helvetica", 64), bg="white", fg="black")

def cancel():
    experiment_window.destroy()

def say_goodbye():
    global label
    label.config(text="Task is Finished. \n Please let the Experimenter know.")
    # Schedule the window to close 2 seconds after showing the goodbye message
    experiment_window.after(2000, experiment_window.destroy)

def start_experiment():
    instruction_window.destroy()  # Close the instruction window
    # Create the main window
    global experiment_window
    experiment_window = tk.Tk()
    experiment_window.attributes('-fullscreen', True)
    experiment_window.configure(background='white')

    experiment_window.after(total_time*1000, say_goodbye)

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

    # Start the Tkinter event loop
    experiment_window.mainloop()

# Create the instruction window
instruction_window = tk.Tk()
instruction_window.attributes('-fullscreen', True)
instruction_window.configure(background='white')
instruction_window.title("Instructions")

style = ttk.Style() # button style for ttk since
style.configure("TButton", background="white", foreground="black", font=("Helvetica", 48))

# Add instructions label
instructions = (
    "TIME ESTIMATION TASK\n\n\n\n"
    "Press the spacebar every 8-12 seconds.\n\n"
    "Estimate the time but do not count seconds.\n\n"
    "Avoid rhythmic responses and try to be spontaneous.\n\n"
    "Press 'Start' to do a short practice session.\n\n"
)

label = tk.Label(instruction_window, text=instructions, font=("Helvetica", 48), bg="white", fg="black", justify="center")
label.pack(pady=20)

# Add a button to start the experiment
start_button = ttk.Button(
    instruction_window,
    text="Start\nPractice",
    command=start_experiment,
    padding=(10, 5),  # Optional: Adds extra space around the text
    style="TButton"
)
# start_button = tk.Button(instruction_window, text="Start", command=start_experiment, font=("Helvetica", 48))
start_button.pack(pady=20)

# Start the instruction window loop
instruction_window.mainloop()