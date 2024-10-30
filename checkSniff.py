# checkSniff: checks serial port connection to sniffBasic before running shell script to start experiment
# to prevent lost data and other issues due to hardware, connection, experimenter error

# sketch:
#   1. instructions to ensure sniff is fully connected (usb --> computer; air line secure at device and nose)
#   2. click button to check connection
#   2b. Possibly check small (2 second) data feed with visual?
#   3. return either connected or check device connections
#   4. return (using result = subprocess.run(['python3', 'other_script.py'], capture_output=True, text=True)
#      to calling script

## TESTED OK

import tkinter as tk
from tkinter import messagebox
import serial

def first_check():
    # Create a root window (not shown)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Simple instructions and button to check sniff connection
    response = messagebox.askokcancel("Hello", "Ensure sniffBasic is connected to the computer\n"
                           "and the nasal cannula is attached and positioned correctly.\n\n"
                           "Press ok to test that sniffBasic is connected\n"
                                      "or press cancel to abort session")
    print("response received:", response)
    root.destroy()
    return response


def show_warning():  # in case serial port can not be reached during experiment
    # Create a root window (not shown)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    response = messagebox.askokcancel("Not Connected", "unable to connect to sniff serial port.\n"
                           "please check connections and try again (OK),\n"
                           "or (cancel) to abort session if necessary.")
    check_warning_response(response)
    root.destroy()
    if response:
        return(response)

def check_warning_response(response):  # either try again (ok) or terminate entire (inc. parent) session
    if response:
        print("OK clicked. Checking connection again.")
        return(response)
    else:
        print("Canceled. Returning to main Script.")
        return(response)


# response = True  # set response as ok to enable while, is overwritten during loop
response = first_check()

while response:
    # Initialize serial port connection
    print("chjecking serial port....")
    try:
        ser = serial.Serial('/dev/tty.usbmodem20523055584B1', baudrate=9600, timeout=1)
        print("Serial port connected successfully")
        print("writing True to file...")
        with open('sniffCheckStatus.txt', 'w') as f:
            f.write('1')  # connected
        break
        # it is maybe too complex to also check data from the sniff...not enough time before launch
    except serial.SerialException:  # Catch specific serial exceptions
        print("Something not connected...")
        response = show_warning()
    except Exception as e:  # Catch any other general exceptions
        print(f"An unexpected error occurred: {e}")
        response = show_warning()
else:  # if user cancels this check
    print("Terminating sniffCheck...")
    print("writing False to file...")
    # put a write file here with False, and return to exit
    # no data can be collected as user has opted to leave off
    with open('sniffCheckStatus.txt', 'w') as f:
        f.write('0')  # not connected