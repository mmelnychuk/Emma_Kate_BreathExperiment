import serial
import csv
import os
import threading
import sys
import signal
import time

"""This script reads sniffBasic sensor from serial port '/dev/tty.usbmodem20523055584B1'
...it is started using subprocess from calling script and stopped using .terminate().
Sampling rate is 20Hz (threading.Timer(0.05, sniff).start()  # Repeats every 50 ms."""


def show_warning():  # in case serial port can not be reached during experiment
    os.system('osascript -e \'display dialog "Could not reach the serial port." with title "Warning" buttons {"OK"}\'')


# Initialize serial port connection
try:
    ser = serial.Serial('/dev/tty.usbmodem20523055584B1', baudrate=9600, timeout=1)
except:
    show_warning()
    raise IOError("Could not connect to given port")


def handle_sigterm(signum, frame):  # catch terminate() (sigterm) call and close serial port
    ser.close()
    print("Serial port closed")
    exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


file_path = sys.argv[1]  # file path from calling script

# Initialize the CSV file and temp file (for Atomic Write) with headers
# make directory if it doesn't exist
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# file for pipeline real time reads
with open(file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    # headers
    writer.writerow(['Unix Time', 'Nasal Pressure'])


# Write csv in append mode
def write_csv(file_path, data):
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def parse_data(data: str):
    """Parse the given raw data string and return pressure in Pascal
    Args:data (String): the raw data received from the basic via serial port
    Returns:double: the pressure value in Pascal"""

    try:
        # data = int(data.split()[0])
        data = (data.split()[0])
        # print(data)
        data = data.strip()
        data = int(data)
        data = -data / 1000
    except Exception as e: # catch any fail
        Data = 0
    return data


def sniff():
    y = 0  # init y in case of exception
    try:
        # Read data from serial port
        data = ser.readline()
        ser.reset_input_buffer()

        # print(string_value)
        string_value = data.decode('utf-8').strip()

        # parse data
        data = parse_data(string_value)

        if data:
            y = data
        else:
            y = 0
            raise ValueError("No data received")

    except serial.SerialTimeoutException:  # to stop thread accumulation
        y = 0
        # print("Timeout occurred")
    except (serial.SerialException, ValueError) as e:
        y = 0
        # print(f"Error: {e}, using default values (y={y})")

    unix_time = (time.time())
    data_to_write = [unix_time, y]

    write_csv(file_path, data_to_write)

    threading.Timer(0.05, sniff).start()  # Repeats every 50 ms

# one sniff every 50 ms until terminated
sniff()
