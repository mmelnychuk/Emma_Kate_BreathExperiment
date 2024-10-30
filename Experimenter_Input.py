
# dialogue to gather participant id and task times
# task times (except AUT) are left as user-defined
# for flexibility if needed
# calls sniffCheck (to check sniff connectivity before proceeding)
# to minimize data loss
## TESTED OK (with sniffCheck.py)

import sys
print(sys.executable) # for testing problems with pyserial in venv


import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
import os
import json
import runpy
import subprocess

# root = tk.Tk()
# root.withdraw()  # Hide the root window -- for messagebox use later in script, etc


def get_task_times():
    # Create the root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask for participant ID
    participant_id = simpledialog.askstring("Input", "Enter Participant ID:")

    # Ask for task times in seconds
    task_1_time = simpledialog.askinteger("Input", "Kornhuber Time (in seconds):")
    task_2_time = simpledialog.askinteger("Input", "Meditation Time (in seconds):")
    # task_3_time = simpledialog.askinteger("Input", "AUT is set to default\n to 6 words, 3 minutes each.\n enter 0")
        # task_3_time probably not needed bc AUT is set at n words and fixed time constraints
    order_string = simpledialog.askstring("Input", "Task Order (eg. 3,1,2)\nkornhuber=1; meditaiton=2; AUT=3:")

    if order_string:
        # Convert the input string to a list of integers
        task_order = [int(num.strip()) for num in order_string.split(",")]

    # Close the root window
    root.destroy()

    # Return the values as a dictionary
    return {
        "participant_id": participant_id,
        "task_1_time": task_1_time,
        "task_2_time": task_2_time,
        # "task_3_time": task_3_time,
        "task_order": task_order
    }


def check_sniff():
    runpy.run_path('checkSniff.py')
    # subprocess.run(['python3', 'checkSniff.py'])
    with open(f'sniffCheckStatus.txt', 'r') as f:
        status = int(f.read())
    if status == 1:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("sniff status", "sniffBasic is connected.\n"
                                       "Press 'ok' to continue with setup.")
        root.destroy()
        return()
    else:
        root = tk.Tk()
        root.withdraw()
        response = messagebox.askokcancel("sniff status", "sniffBasic is either NOT connected,\n"
                                                          "and/or you have canceled the check.\n\n"
                               "Press 'ok' to check again,"
                               "or press 'cancel' to abort setup completely.")
        root.destroy()
        if response:  # recursive loop
            check_sniff()
        else:
            exit()
    print('checkSniff completes')
    # root.destroy()

def next_task():
    root.destroy()


def next_session():
    global root
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(background='white')
    label = tk.Label(root, text="Please alert the experimenter.",
                     font=("Helvetica", 64), bg="white", fg="black")
    label.pack(pady=20, expand=True)

    # Button to trigger the next session dialog
    start_button = tk.Button(root, text="Continue", font=("Helvetica", 24), command=next_task)
    start_button.pack(pady=20)

    root.mainloop()


def kornhuber_practice():
    runpy.run_path('Kornhuber_Practice.py')
    next_session()


def kornhuber():

    # run kh task, pass vars
    # subprocess.run(['python3', 'KORNHUBER_Exp.py'])
    # os.system('python3 KORNHUBER_Exp.py')
    # exec(open('KORNHUBER_Exp.py').read())
    runpy.run_path('KORNHUBER_Exp.py')
    next_session()
    # run kh practice from kh-exp


def mw():
    # exec(open('mw_meditation_selfAlert.py').read())
    runpy.run_path('mw_meditation_selfAlert.py')
    next_session() 

def aut():
    # exec(open('Alt_Use_Task.py').read())
    runpy.run_path('Alt_Use_Task.py')
    next_session()

def run_tasks_in_order(task_order):
    # Map integers to task functions
    task_mapping = {
        1: [kornhuber_practice, kornhuber],
        2: [mw],
        3: [aut]
    }

    # Execute tasks in the order specified by the user
    for task_number in task_order:
        task_funcs = task_mapping.get(task_number)
        print(task_funcs)  # Print the list of functions for debugging
        if task_funcs:  # Check if any functions were found
            for task_func in task_funcs:  # Iterate through the list of functions
                task_func()  # Call each function


# Main Loop
if __name__ == "__main__":
    # print("Current working directory:" -- to check pwd
    os.getcwd()

    # check that sniff basic is connected (and reading data)
    check_sniff()

    task_data = get_task_times()
    print(task_data)
    # Now you can pass task_data['participant_id'], task_data['task_1_time'], etc. to other scripts or functions.
    # Write to file and each task will read
    with open(f'task_data.json', 'w') as f:
        json.dump(task_data, f)

    # make dir for data and subject folder
    # Specify the directory path
    directory = f'subject_data/{task_data["participant_id"]}'

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Run each experimental task
    # Function to run tasks based on user input

    task_order = task_data["task_order"]

    print(task_order)

    run_tasks_in_order(task_order)

    os.remove('task_data.json')
    # # Kornhuber
    # # root.destroy()
    # kornhuber_practice()  # practice (60s?)
    #
    # # Next Task
    # # root.destroy()
    # root = tk.Tk()
    # root.attributes('-fullscreen', True)
    # root.configure(background='white')
    # label = tk.Label(root, text="Please alert the experimenter.",
    #                  font=("Helvetica", 64), bg="white", fg="black")
    # label.pack(pady=20, expand=True)
    #
    # # Button to trigger the next session dialog
    # start_button = tk.Button(root, text="Next Task", font=("Helvetica", 36), command=next_session)
    # start_button.pack(pady=50)
    #
    # root.mainloop()
    #
    #
    # kornhuber()  # full task
    #
    # # Next Task
    # root = tk.Tk()
    # root.attributes('-fullscreen', True)
    # root.configure(background='white')
    # label = tk.Label(root, text="Please alert the experimenter.",
    #                  font=("Helvetica", 64), bg="white", fg="black")
    # label.pack(pady=20, expand=True)
    #
    # # Button to trigger the next session dialog
    # start_button = tk.Button(root, text="Next Task", font=("Helvetica", 36), command=next_session)
    # start_button.pack(pady=50)
    #
    # root.mainloop()
    #
    #
    # print('what is going on here?')
    #
    # # # MW task
    # mw()
    #
    # # Next Task
    # root = tk.Tk()
    # root.attributes('-fullscreen', True)
    # root.configure(background='white')
    # label = tk.Label(root, text="Please alert the experimenter.",
    #                  font=("Helvetica", 64), bg="white", fg="black")
    # label.pack(pady=20, expand=True)
    #
    # # Button to trigger the next session dialog
    # start_button = tk.Button(root, text="Next Task", font=("Helvetica", 36), command=next_session)
    # start_button.pack(pady=20)
    #
    # root.mainloop()
    #
    #
    # # # AUT
    # aut()

    # clean up temp file with participant parameters
