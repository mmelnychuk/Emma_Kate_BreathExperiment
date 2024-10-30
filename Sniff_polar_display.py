# SniffDiff,
# Michael C. Melnychuk, June/July 2024:
# reads serial port data from sniffLogic Basic,
# plots data and derivatives, and calculates instantaneous respiratory phase angle.
# SniffScience app was not appropriate for our purposes so I created one that was.
# This version constructs a respiratory trace from the nasal flow data of the device.
# It does not call (or require) the SniffLogic SDK, but reference was made to it early on.
# While naso-oral airflow and respiratory volume should normally be a near-perfect derivative-integral pair
# this is not the case here, most likely due to sensor nonlinearity and/or turbulence
# differences between inhale and exhale (see workarounds and calibrations explained below),
# so the relationship is more complex than is ideally the case.
#
# When used as a called function, approxiately 10 seconds calibration is required for the
#resp amplitude and resp phase algorithms to settle into acceptable stability.
# this is for presentation purposed, ie asking for stimulus triggers.
# data will be saved, so time can be sync'd with an external program without issue,
#but a brief calibration period is required before any accuracy can be expected
# for phase approximation. (all values are approximate and require further testing
#etc).
#
# The main goal of the current version was to extract respiratory phase from a transformed
# respiratory time series to allow probe or stimulus injections at specific resp phases
# and to that end was successful, albeit with a nominal margin of phase-wise error, due to
# as mentioned sensor/turbulence issues, and standard idiosyncrasies of the Hilbert Transform
# in the case of variable frequency/amplitude signals, as well as slight non-stationarity
# issues with signal drift due to inadequate calibration, and initial (internal) calibration.
#
# This code can be called from presentation software or run in parallel by a master program,
# either one of which can call the phase value from this script (easy mods). The visualization
# should be locked out in this case (possibly with an added arg, or comment out plt.show()).
# The structure of the program however, requires the funcAnimation function to run, as the update
# function is controlled by the animation function.
#
# The visualization:
# 3 animated plots: 1) nasal airflow (pressure); 2) respiratory (similar to biosemi resp belt)
# time series; 3) polar plot with phase angle of respiration (theta), airflow magnitude (r), and
# a variable color plotted depending on the magnitude of airflow (pos --> red, neg --> blue,
# nil or nearly nil (apnea) --> gray).
#
# Nasal pressure was chosen as the radial axis (r) as it shares less mutual information with
# respiratory phase than diphragmatic volume, and thus provides more information
#
# Future Versions:
# The SniffBasic is single sensor and gives one reading for both nostrils and none
# for mouth. The Holter Monitor will apparently have 3 sensors, which are easily
# adapted here, i.e, three plots in the viz display for each air route and 3 returned
# phase/amplitude/frequency/etc values. It is worth noting that
# mouth breathing with the current device still registers pressure at the nostrils,
# as most mouth breathing has a nasal component. Though significantly lower in amplitude,
# phase in the polar plot is highly conserved, as most mouth breathing has a nasal component (it is
# not either/or).

import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import hilbert, detrend
import os
import time
import csv

# Initialize serial port connection
try:
    ser = serial.Serial('/dev/tty.usbmodem20523055584B1', baudrate=9600, timeout=1)
except:
    raise IOError("Could not connect to given port")

file_path = 'sniff/sniff_resp_data.csv'
# temp_path = file_path + '.tmp'

# ----------

# Initialize the CSV file and temp file (for Atomic Write) with headers
# make directory if it doesn't exist
os.makedirs(os.path.dirname(file_path), exist_ok=True)
# file for pipeline real time reads
with open(file_path, 'w', newline='') as file:
    writer = csv.writer(file)
    # headers
    writer.writerow(['Unix Time', 'Nasal Pressure', 'Diaphragm', 'Phase(0-2p)'])
# temp file to flip to ensure data integrity of main (file_path) file
# with open(temp_path, 'w', newline='') as file:
#     writer = csv.writer(file)
#     # headers
#     writer.writerow(['Unix Time', 'Nasal Pressure', 'Diaphragm', 'Phase(0-2p)'])
#         #Note: *** UnixTime not necessarily sync'd between devices ***

# ----------

# Write csv in append mode (during frame - post transforms - in update from funcAnimation)
def write_csv(file_path, data):

    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(data)


# Function to calculate interval from frequency in Hz
# def calculate_interval(frequency_hz):
#     return 1000 / frequency_hz

# Create a figure with specified size
fig = plt.figure(figsize=(15, 5))

polar_lim = ([-1, 4]) #polar chart limits

# Create (left, phase angle)) polar subplot
ax_phase = fig.add_subplot(131, projection='polar')
ax_phase.set_ylim(polar_lim)
ax_phase.set_title('Respiratory Phase Angle\n and Nasal Pressure')

ax_phase.set_xticklabels(['Inhale', '', 'Trough', '', 'Exhale', '', 'Peak'])

# Create (center, respiratory trace) Cartesian subplot
ax_resp = fig.add_subplot(132)
ax_resp.set_xlim(0, 2 * np.pi)
ax_resp.set_ylim(-1, 1)
ax_resp.set_title('Simulated Diaphragmatic Amplitude')

# Create (right, nasal air flow) Cartesian subplot
ax_nasal = fig.add_subplot(133)
ax_nasal.set_xlim(0, 2 * np.pi)
ax_nasal.set_ylim(-2, 2)
ax_nasal.set_title('Nasal Airflow')

plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

# Initialize the lines for all 3 plots
line_phase, = ax_phase.plot([], [], 'ro')
line_origin, = ax_phase.plot([], [], 'r-')  # Line from origin to point
line_resp, = ax_resp.plot([], [], 'b-')
line_nasal, = ax_nasal.plot([], [], 'b-')


# Update function with stop condition and error handling
max_updates = 100000  # Maximum number of updates
update_count = 0
# define variables
x = 1
y=0
nasal_sum = 0
xdata, ydata = [], []
resp_ydata = []
polar_origin_ydata = []
polar_angle_ydata = []


# initialize the plots
def init():
    line_phase.set_data([], [])
    line_origin.set_data([], [])
    line_resp.set_data([], [])
    line_nasal.set_data([], [])

    return line_phase, line_origin, line_resp, line_nasal,

def parse_data(data: str):
    """Parse the given raw data string and return pressure in Pascal
    Args:
        data (String): the raw data received from the basic via serial port
    Returns:
        double: the pressure value in Pascal"""
    # data = int(data.split()[0])
    data = (data.split()[0])
    # print(data)
    data=data.strip()
    data = int(data)
    data = -data / 1000
    return data


# Function to update the plots in each frame
def update(frame):
    global file_path, update_count, nasal_sum
    global x, y, xdata, ydata, resp_ydata, polar_origin_ydata, polar_angle_ydata
    global line_phase, line_origin
    if update_count >= max_updates:
        ani.event_source.stop()
        return line_phase, line_origin, line_resp, line_nasal,

    try:
        # Read data from serial port

        data = ser.readline()
        ser.reset_input_buffer()

        string_value = data.decode('utf-8').strip()
        # print(string_value)

        data = parse_data(string_value)
        # print(data)

        if data:
            y = data
        else:
            y=0
            raise ValueError("No data received")

    except (serial.SerialException, ValueError) as e:
        print(f"Error: {e}, using default values (x={x}, y={y})")
    x += 1
    # print(x, y)

    #nasal data
    xdata.append(x)
    ydata.append(y)
    print("X length: ", len(xdata))

    # set data for plotting
    line_nasal.set_data(xdata, ydata)
    # Adjust xy-axes limits
    ax_nasal.set_xlim(0, len(xdata)+1)
    ax_nasal.set_ylim(np.min(ydata) - 0.1, np.max(ydata) + 0.1)

    #resp data
    #needs to be scaled b/c of nonlinear velocity/pressure/sensor effects
    #see also above scaling method
    # inhale is greater integral than exhale (so signal drift upward)
    # inhale and exhale both exhibit nonlinear changes with respiratory effort
    # here we divide value by a function of its absolute magnitude (above), and
    # also scale inhale relative to exhale by a constant
    # resp series is also detrended (nasal pressure is not)
    # current outputs are decent approximation (but need to be co-registered with resp belt)
    # at some point
    # print (type(y))
    if y > 0:
        y = y*.9  # scales back inhale flow due to inherent sensor (prob turbulence) bias
        # print("SCALED Y = ", y)
    if y==0:
        y=.0001 # avoid div by zero error
    y = (y/abs(y))*np.sqrt(abs(y)) # further scaling for nonlinear sensor response

    # print("Y = ", y)

    nasal_sum = nasal_sum + y # integrates nasal signal --> gives resp trace
    # print("Nasal Sum = ", nasal_sum)
    # print("Nasal Sum Type: ", type(nasal_sum))
    resp_ydata.append(nasal_sum)
    resp_ydata_dt = detrend(np.array(resp_ydata))
    line_resp.set_data(xdata, detrend(resp_ydata_dt))
    # Adjust xy-axes limits
    ax_resp.set_xlim(0, len(xdata) + 1)
    ax_resp.set_ylim(np.min(resp_ydata_dt) - 0.1, np.max(resp_ydata_dt) + 0.1)

    # polar plot (resp phase angle and airflow (or resp volume?)
    if update_count > 50: # wait to get reasonable phase transform?
        resp_phase = hilbert(detrend(np.array(resp_ydata[-50:])))
        polar_angle_ydata = np.unwrap(np.angle(resp_phase))
        # polar_angle_ydata = np.mod(polar_angle_ydata, 2*np.pi)
        polar_angle_ydata = polar_angle_ydata.tolist()
        # print("polar angle type: ", type(polar_angle_ydata))
        # print(polar_angle_ydata[-1])
        # Calculate the mean and standard deviation of nasal airflow to get z-scores
        # scale numbers for presentation
        mean = np.mean(np.array(ydata))
        std_dev = np.std(np.array(ydata))

        # Standardize the signal
        norm_ydata = (np.array(ydata) - mean) / std_dev
        # print("norm_ydata: ", norm_ydata)
        # norm_ydata = np.array(norm_ydata)
        # print("norm_ydata TYPE: ", type(norm_ydata))
        norm_ydata = norm_ydata.tolist()

        # print("polar data: ", polar_angle_ydata[-1], norm_ydata[-1])

        line_phase.set_data([polar_angle_ydata[-1]], [abs(norm_ydata[-1])])
        line_origin.set_data([0, polar_angle_ydata[-1]], [polar_lim[0], abs(norm_ydata[-1])])

        # change plot color for inhale (red) v exhale (blue) v apnea (gray)
        # values will need to be changed along with calibration parameters
        # this is a rough arbitrary outline for testing
        if y < -1: # exhale --> blue
            line_phase.set_color('blue')
            line_origin.set_color('blue')
        elif y > 1: # inhale --> red
            line_phase.set_color('red')
            line_origin.set_color('red')  # Line from origin to point
        else: # low or nil breath --> gray
            line_phase.set_color('gray')
            line_origin.set_color('gray')
        # print("Y value for polar plot = ", norm_ydata[-1])

        # # Example for mind wandering probe or stimulus injection at specific respiratory phase
        # # Needs specification and comms (args, returns) in/with master (presentation) program
        # mod_phase = np.mod(polar_angle_ydata[-1], 2 * np.pi)
        # if (3*np.pi)/2 < mod_phase < 2*np.pi:
        #     print ("---------INJECTING PROBE!!!---------")
# ------------------
# ------------------

        # Set up data to write real-time to file (accessible by other apps, like MW probe, etc)
        # Get Unix Time
        wTime = time.time() * 1000

        # Nasal Pressure
        wNasal = y # seems local so should be able to do that??

        # Diaphragm Trace (normal to us resp curve)
        wDiaphragm = nasal_sum


        # Polar (phase) angle of the diaphragm trace
        # sends a neutral value until enough data has been collected
        # to give a meaningful value
        # note to developers: wait at least this long to begin experimental work
        if update_count <= 50:
            wPolar = np.pi
        else: # if calibration is "finished"
            wPolar = polar_angle_ydata[-1]

        # gather these outputs to a single output variable
        data_row_to_write = [wTime, wNasal, wDiaphragm, wPolar]
        print (data_row_to_write)

        write_csv(file_path, data_row_to_write)




    update_count += 1

    return line_phase, line_origin, line_resp, line_nasal
    # END UPDATE

# Create the animation
ani = animation.FuncAnimation(fig, update, interval=5, init_func=init, blit=False)

# Show the animation
plt.show()
# Save the animation to a file
ani.save('/Users/joanne/PycharmProjects/sniff/sniff_animation.mp4', writer='ffmpeg')