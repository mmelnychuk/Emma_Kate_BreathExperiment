import tkinter as tk
import time
from tkinter import simpledialog
from datetime import datetime
import os
import json
import csv
import subprocess
import atexit

countdown_timer_seconds = 180  # Default to 180 s / 3 min
# Can exit experiment with Esc key
fontsize = 20

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set the window to full screen
        # Get the screen's width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.configure(background='white')
        #
        # # Set the geometry to fullscreen (width x height)
        self.geometry(f"{screen_width}x{screen_height}")

        # Set root attributes to hide Dock and Menu Bar on macOS
        self.attributes('-topmost', True)  # Keep window on top
        self.attributes('-fullscreen', True)  # This can still be used to hide menu bar
        self.configure(background='white')

        # self.geometry("1200x700")

        # Optionally hide the title bar
        # self.overrideredirect(True)

        self.title("AUT")


        # Ask for participant number
        # self.participant_number = self.ask_for_participant_number()
        # remove ralph's dialogue window and get sub id from file

        # get vars from json file
        # Read from file
        with open(f'task_data.json', 'r') as f:
            task_data = json.load(f)
            print('aut:', task_data)
            print('trying to read from file')
        if task_data:
            self.participant_number = task_data["participant_id"]
            print(self.participant_number)
        else:
            self.participant_number = "participant"
            print(self.participant_number)

        if self.participant_number is None:
            print ('something went wrong reading task_data')
            self.destroy()  # Exit if no input is provided
            return

        # Ensure 'data' folder exists
        self.ensure_data_folder()

        # Create a new file with a timestamp and participant number
        self.responses_file = self.create_new_file()
        print(self.responses_file)

        # Initialize the frames and display the first screen
        self.frames = {}

        # Configure grid to ensure frames expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(FirstScreen)

        # Set Esc as exit key
        self.bind('<Escape>', self.close_window)

    def ask_for_participant_number(self):
        # should be able to inject participant_ID from control script here???
        """Open a dialog box to ask for the participant number."""
        # changed to read from file created in Experimenter_Input
        #
        try:
            with open(f'task_data.json', 'r') as f:
                task_data = json.load(f)
            if task_data:
                participant_number = task_data["participant_id"]

                print(task_data)
        except:
            participant_number = "participant"
        return participant_number

    def restore_window(self):
        """Restore the window after participant number is entered."""
        self.deiconify()  # Show the main window
        self.lift()  # Bring window to the top

    def ensure_data_folder(self):
        # maybe need to change
        """Ensure the 'data' folder exists."""
        # if not os.path.exists("subject_data"):
        #     os.makedirs("subject_data")
        # redundant with create_new_file below

    def create_new_file(self):
        # maybe need to change
        """Create a new file with a timestamp and participant number in the filename."""
        # timestamp = datetime.now().strftime("%d%m%Y_%H%M")
        # filename = f"data/{self.participant_number}_{timestamp}_AUTresponses.txt"
        # # Open the file in write mode
        # file = open(filename, "w")

        # file to save results to
        filename = f'subject_data/{self.participant_number}/AUT.txt'
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # ensure_data_folder redundant
        global sniff_filename
        sniff_filename = f'subject_data/{self.participant_number}/AUT_sniff.csv'

        # Write the start timestamp in Unix time format
        # start_unix_time = int(time.time())  # Get the current Unix timestamp
        # file.write(f"task_start_time: {start_unix_time}")

        # with open(filename, 'w', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerow(['UnixTime'])

        file = open(filename, "w")

        return file

    def show_frame(self, screen_class):
        """Show a frame based on the screen class."""
        frame = self.frames.get(screen_class)
        if frame is None:
            # Create a new frame if it does not exist
            frame = screen_class(self)
            self.frames[screen_class] = frame
            frame.grid(row=0, column=0, sticky="nsew")  # Use grid to ensure proper sizing
        frame.tkraise()

    def close_window(self, event=None):
        """Close the application and ensure the file is closed."""
        if hasattr(self, 'responses_file'):
            self.responses_file.close()
            process.terminate()
        self.destroy()

class CountdownFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.time_remaining = countdown_timer_seconds
        self.timer_label = tk.Label(self, text=self.format_time(self.time_remaining), font=('Verdana', fontsize))
        self.timer_label.place(relx=0.5, rely=0.3, anchor='center')

        # Timer state
        self.running = True

        # Variable to store user input
        self.user_input = ""

        # Label to display user input
        self.input_label = tk.Label(self, text="", font=('Verdana', fontsize))
        self.input_label.place(relx=0.5, rely=0.6, anchor='center')

        # Flag to indicate if key presses should be ignored
        self.ignore_key_presses = False

        # Initialize and start the countdown timer
        self.update_timer()

        # Timer for resuming countdown if no keys are pressed
        self.resume_timer_id = None

        # Bind spacebar to toggle the timer
        self.master.bind('<space>', self.toggle_timer)

        # Bind key responses only when the timer is paused
        self.master.bind('<Key>', self.handle_key_press)

    def format_time(self, seconds):
        """Format the time in minutes and seconds."""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self):
        """Update the countdown timer."""
        if self.running and self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=self.format_time(self.time_remaining))
            self.after(1000, self.update_timer)  # Update the timer every 1000ms (1 second)
        elif self.time_remaining == 0:
            self.timer_label.config(text="00:00")
            self.handle_timer_up()  # Call this method when the timer is up
            self.running=False

    def toggle_timer(self, event):
        """Pause the countdown timer when spacebar is pressed."""
        if self.running:
            self.running = False
            # When paused, enable key responses
            self.master.bind('<Key>', self.handle_key_press)
            # Start the timer to resume countdown if no keys are pressed for 5 seconds
            self.start_resume_timer()
        else:
            # Prevent resuming the timer with spacebar
            self.handle_key_press(event)

    def handle_key_press(self, event):
        """Handle key presses only when the timer is paused."""
        if self.ignore_key_presses:
            return  # Ignore all key presses if the flag is set

        if not self.running:
            if event.keysym == 'Return':  # Enter key pressed
                self.handle_enter_key()
            elif event.keysym == 'BackSpace':  # Handle backspace key
                self.user_input = self.user_input[:-1]
            elif event.keysym == 'space':  # Handle spacebar key
                self.user_input += ' '
            else:
                if event.char:
                    self.user_input += event.char  # Append the character to the user input
                    # Wrap text if the current line length exceeds 50 characters without splitting words
                    lines = self.user_input.split("\n")
                    current_line = lines[-1]
                    if len(current_line) > 100:
                        last_space_index = current_line.rfind(" ")
                        if last_space_index != -1:
                            lines[-1] = current_line[:last_space_index]
                            lines.append(current_line[last_space_index + 1:])
                            self.user_input = "\n".join(lines)
            # Update the input label with the current user input
            self.input_label.config(text=self.user_input)
            # Restart the resume timer each time a key is pressed
            self.start_resume_timer()

    def start_resume_timer(self):
        """Start the timer to resume the countdown if no keys are pressed for 5 seconds."""
        if self.resume_timer_id:
            self.master.after_cancel(self.resume_timer_id)
        self.resume_timer_id = self.master.after(5000, self.resume_countdown)

    def resume_countdown(self):
        """Resume the countdown timer."""
        if not self.running:
            self.running = True
            self.update_timer()

    def handle_enter_key(self):
        """Handle Enter key press, to be implemented by subclasses."""
        pass

    def handle_timer_up(self):
        """Method to handle what happens when the timer is up."""
        self.ignore_key_presses = True
        # This method should be overridden by subclasses
        pass


class FirstScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        instructions = tk.Label(self, font=("Verdana", fontsize), bg="white", fg="black",
                                text="""Welcome to the Alternative Uses Task. 

        In this task, you will be asked to generate as many alternative uses 
        as you can for a given object. You are encouraged come up with
        as many creative and original uses as possible. There are no right or
        wrong answers, so be as imaginative as you can!

        For each item you will have 3 minutes. A countdown timer will be displayed on the screen.
        As soon as you have a clear idea, press the spacebar. This will pause the timer.
        In this study we are interested in the precise timing of when ideas are generated. So please
        press the SPACEBAR as soon as you generate your alternative use, and then type it in.
        To submit your response, you will press the ENTER key, which will restart the timer.
        The timer will automatically continue if no key is pressed for 5 seconds while the timer is paused.
        
        There is a practice exercise on the next screen so familiarise you with the response method.
        After this, you will be presented with the 6 items for the task.

        Click below to continue to the practice exercise"""
                                )
        instructions.place(relx=0.5, rely=0.45, anchor='center')

        ptc1 = tk.Button(self, text="Continue to practice",
                         font=("Verdana", fontsize),
                         command=lambda: self.master.show_frame(SecondScreen))
        ptc1.place(relx=0.5, rely=0.7, anchor='center')


class SecondScreen(CountdownFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="""This is a practice response. 
        Press the SPACEBAR to pause the timer, type the word 'response', and then press ENTER""",
                 font=('Verdana', fontsize)).place(relx=0.5, rely=0.4, anchor='center')

        # Create the button and store a reference to it
        self.response_button = tk.Button(self, text="", command=lambda: self.master.show_frame(ThirdScreen),
                                         font=('Verdana', fontsize))
        self.response_button.place_forget()  # Initially hide the button

    def handle_timer_up(self):
        pass

    def handle_enter_key(self):
        """Handle Enter key press."""
        if self.user_input.strip():
            self.response_button.config(text="Continue to next instructions")
            self.response_button.place(relx=0.5, rely=0.7, anchor='center')  # Show the button
            self.user_input = ""
            self.input_label.config(text="")


class ThirdScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        instructions = tk.Label(self, font=("Verdana", fontsize),
                                text="""You may now begin the task. You will see 6 items in total, 3 minutes for each item. 

        Please ensure you press the SPACEBAR at the precise time that you have the idea, as best as you can. 
        Then, type the response, and press ENTER to submit the response, and then the timer will continue.
        The timer will automatically continue if no key is pressed for 5 seconds while the timer is paused.
        
        If you have any further questions, please ask the experimenter now.
        Otherwise, press below to begin the task"""
                                )
        instructions.place(relx=0.5, rely=0.45, anchor='center')

        ptc2 = tk.Button(self, text="Continue to task",
                         font=("Verdana", fontsize),
                         command=lambda: self.master.show_frame(FourthScreen))
        ptc2.place(relx=0.5, rely=0.7, anchor='center')


class FourthScreen(CountdownFrame):
    def __init__(self, parent):

        # start sniffing
        global process
        process = subprocess.Popen(['python3', 'getSniffs.py', sniff_filename])

        # Ensure subprocesses are terminated if and when the main script exits
        def terminate_subprocess():
            process.terminate()

        atexit.register(terminate_subprocess)  # this will kill getSniffs and 'signal will close serial port connection

        self.responses_file = parent.responses_file  # Get the file reference from the parent
        self.words = ["paperclip", "brick", "spoon", "rubber band", "newspaper", "suitcase"]
        self.current_word_index = 0
        self.word_recorded = False  # Initialize the flag to track if the word has been recorded
        super().__init__(parent)
        self.create_widgets()
        # Record current word
        self.responses_file.write(f"\nword: {self.words[self.current_word_index]}\n")
        timestamp = time.time()  # Get the current Unix timestamp *changed this from integer to real unix time for precision
        print(timestamp)
        self.responses_file.write(f"word_timestamp: {timestamp}\n")

    def create_widgets(self):
        # Create the label with initial word
        self.word_label = tk.Label(self, text=self.get_current_word(),
                                   font=('Verdana', fontsize))
        self.word_label.place(relx=0.5, rely=0.4, anchor='center')

        # Create the button and store a reference to it
        self.response_button = tk.Button(self, text="Continue to the next word",
                                         command=self.next_word, font=('Verdana', fontsize))
        self.response_button.place_forget()  # Initially hide the button

    def get_current_word(self):
        """Return the current word from the list."""
        return f"Name uses for a...\n\n{self.words[self.current_word_index]}"

    def toggle_timer(self, event):
        super().toggle_timer(event)
        timestamp = time.time()  # Get the current Unix timestamp **changed to real utx for precision
        self.responses_file.write(f"paused_timestamp: {timestamp}\n")

    def update_timer(self):
        """Update the countdown timer and manage key press ignoring."""
        super().update_timer()  # Call the base class method
        if not self.running and self.time_remaining <= 0:
            self.ignore_key_presses = True
            self.master.bind('<Key>', lambda event: None)  # Prevent all key presses

    def handle_timer_up(self):
        """Handle the event when the timer is up."""
        if self.current_word_index == len(self.words)-1:
            self.is_final_word()
        # Show the response button when the timer is up
        self.response_button.place(relx=0.5, rely=0.7, anchor='center')
        # Set the flag to ignore key presses
        self.ignore_key_presses = True

    def handle_enter_key(self):
        """Handle Enter key press."""
        if self.user_input.strip():
            # Save the user input to the file
            self.responses_file.write(f"response: {self.user_input.strip()}\n")
            timestamp = time.time()  # Get the current Unix timestamp **changed to real utx for precision
            self.responses_file.write(f"entered_timestamp: {timestamp}\n")

            # Reset user input and update the input label
            self.user_input = ""
            self.input_label.config(text="")

            # Resume the timer
            self.running = True
            self.update_timer()

    def next_word(self):
        """Move to the next word in the list and reset the timer."""
        self.current_word_index += 1

        # Update the label with the new word
        self.word_label.config(text=self.get_current_word())
        self.word_recorded = False  # Reset the flag for the new word
        # Reset the timer
        self.time_remaining = countdown_timer_seconds
        self.timer_label.config(text=self.format_time(self.time_remaining))
        self.running = True
        self.update_timer()

        self.response_button.place_forget()  # Hide the button

        # Record current word
        self.responses_file.write(f"\nword: {self.words[self.current_word_index]}\n")
        timestamp = time.time()  # Get the current Unix timestamp **changed to real utx for precision
        self.responses_file.write(f"timestamp: {timestamp}\n")

        # Clear user input and update the input label
        self.user_input = ""
        self.input_label.config(text="")

        # Allow key presses again
        self.ignore_key_presses = False

    def is_final_word(self):
        """Handle the final word scenario."""
        self.response_button.config(text="Continue", command=self.go_to_fifth_screen)
        self.response_button.place(relx=0.5, rely=0.7, anchor='center')
        self.response_button.update()  # Force update the button to reflect changes

    def go_to_fifth_screen(self):
        """Transition to the FifthScreen."""
        self.master.show_frame(FifthScreen)

class FifthScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.responses_file = parent.responses_file  # Get the file reference from the parent

    def create_widgets(self):
        # Example final message
        final_message = """That is the end of the task, thank you very much for taking part.
    Let the experimenter know you have finished."""
        self.message_label = tk.Label(self, text=final_message, font=("Verdana", fontsize))
        self.message_label.place(relx=0.5, rely=0.5, anchor='center')

        # Button to exit the application
        self.exit_button = tk.Button(self, text="Exit", command=self.close_experiment, font=("Verdana", fontsize))
        self.exit_button.place(relx=0.5,rely=0.6, anchor='center')

    def close_experiment(self):
        """Close the application."""
        # Write the end timestamp in Unix time format
        end_unix_time = time.time()  # Get the current Unix timestamp **changed to real utx for precision
        self.responses_file.write(f"task end time: {end_unix_time}\n")
        self.master.close_window()

# if __name__ == "__main__":
print('aut has started')
app = Application()
app.mainloop()
