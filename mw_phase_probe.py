import tkinter as tk
import time

def show_input():
    input_text = entry.get()
    unix_time = (time.time())
    label.config(text=f"You responded... {input_text} @ {unix_time}")
    label.pack(expand=True)  # Center the label in the window

def cancel():
    root.destroy()

# Create the main window
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(background='white')

# Create a label with initial text
label = tk.Label(root, text="Was your mind on your breath?", font=("Helvetica", 32), bg="white", fg="black")
label.pack(pady=20, expand=True)

# Create an entry widget for user input
entry = tk.Entry(root, font=("Helvetica", 24), bg="white", fg="black")
entry.pack(pady=20)
entry.focus_set()  # Set focus to the entry widget

# Create a button to submit the input
submit_button = tk.Button(root, text="Submit", font=("Helvetica", 24), command=show_input)
submit_button.pack(pady=20)

# Create a button to cancel and close the application
cancel_button = tk.Button(root, text="Cancel", font=("Helvetica", 24), command=cancel)
cancel_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
