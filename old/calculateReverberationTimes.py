from scipy import signal, stats
import numpy as np
from numpy.fft import irfft

from bokeh.plotting import figure, output_file, show, save
from bokeh.layouts import column, gridplot
from bokeh.models import Label
# select a palette
from bokeh.palettes import Dark2_5 as palette
# itertools handles the cycling
import itertools
# create a color iterator
colors = itertools.cycle(palette)
import csv
import pandas as pd
import sys
sys.path.insert(1, r"D:\Scripts\standards\standards")
import filterAndBands
import helpers

## Put a 'try' in this to return RT =0 rather than crashing

def performRTcalculation(data, db_decay='t20', decay_time=5):
    # Set path to configuration file - needs to be absolute for executable
    config_data = helpers.parseConfigFile(path=r'D:\Scripts\reverb-tkinter-interface\config.cfg')
    # Read all configuration data
    ao_device_name = config_data['aodevicename']
    ai_device_name = config_data['aidevicename']
    dio_device_name = config_data['diodevicename']
    fs = int(config_data['samplingfrequency'])
    rise_time = float(config_data['risetime'])
    excitation_time = float(config_data['excitationtime'])
    # decay_time = float(config_data['decaytime'])
    mics = config_data['micid']
    channel_name = config_data['micnames']
    analog_output_id = config_data['outputid']
    estRT = float(config_data['estimatedrt'])
    pRef = float(config_data['referencepressure'])
    n_mics = int(config_data['nummics'])
    # Perform ensemble averaging of individual mics for number of runs
    averaged_data = helpers.ensemble_average(raw_data=data, n_mics=n_mics)
    # General parameters
    t_tot = rise_time+excitation_time+decay_time
    N_samp = int(t_tot)*fs
    dt = 1.0/fs
    t_array = np.arange(start=0, stop=t_tot, step=dt)
    wT = estRT/48
    windowN=int(wT*fs)
    print("Length of window: {}".format(windowN))
    total_reverb = {}
    mic_location = [1, 2, 3, 4, 5, 6]
    # Loop through each mic location and calculate reverberation time
    for mic_location_data, color, mic_loc in zip(averaged_data, colors, mic_location):
        # Convert signal into third octave banded signals
        filtered_data = filterAndBands.thirdOctFilters(data=mic_location_data, fs=fs, f_low=100, f_high=5000)
        plots = []
        reverb_time = []
        freq_step = []
        # Step through third octave bands
        for key in filtered_data:
            print("Processing: {}Hz at mic {}".format(key, mic_loc))
            y = filtered_data[key]
            y_log = 10*np.log10((abs(y)**2)/(pRef**2))
            # Apply time weighting window
            # windowed_data = np.convolve(y_log, np.ones((windowN,))/windowN, mode='valid')
            windowed_data = signal.fftconvolve(in1=y_log, in2=np.ones((windowN,))/windowN, mode='valid')
            t_array = np.arange(start=0, stop=len(windowed_data)/fs, step=dt)
            # Calculate level of excitation and start decay curve 5dB below excitation level
            excitation_range = [int((rise_time)*fs), int((rise_time+excitation_time)*fs)]
            excitation_level = filterAndBands.dBavg(windowed_data[excitation_range[0]+int(0.5*fs):excitation_range[1]-int(0.5*fs)])
            trigger_level = excitation_level - 5
            # Calculate background level/level at end of decay and only use data 10dB above this
            ################## Consider using t20/T30 in place of this - have a setting in GUI ######################
            min_decay_level = min(windowed_data[excitation_range[1]:])
            bg_start = len(windowed_data) - 2*fs
            bg_level = filterAndBands.dBavg(windowed_data[bg_start:])
            if db_decay == 't20':
                bg_trigger_level = max([trigger_level - 20, bg_level+5])
            elif db_decay == 't30':
                bg_trigger_level = max([trigger_level - 30, bg_level+5])
            elif db_decay == 'max':
                bg_trigger_level = bg_level + 10
            # Locate the time where the decay curve should start and end from
            ndx_start = np.where(windowed_data[excitation_range[1]:] <= trigger_level)
            decay_start = ndx_start[0][0]
            ndx_end = np.where(windowed_data[excitation_range[1]:] <= bg_trigger_level)
            decay_end = ndx_end[0][0]
            # Perform least squares fit to the decay curve and calculate the reverberation time
            fitting_level = windowed_data[excitation_range[1]+decay_start:excitation_range[1]+decay_end]
            fitting_times = t_array[excitation_range[1]+decay_start:excitation_range[1]+decay_end]
            slope, intercept, r_value, p_value, std_err = stats.linregress(x=fitting_times,y=fitting_level)
            t_plot = np.arange(start=0, stop=rise_time+excitation_time+decay_time, step=0.1)
            y_fitted = slope*t_plot + intercept
            RT = -60/slope
            reverb_time.append(RT)
            freq_step.append(key)
            print("Reverberation Time: {}s".format(RT))

        total_reverb[mic_loc] = reverb_time
    # Store reverb times and calculate mean statistics
    RT_df = pd.DataFrame.from_dict(total_reverb, orient='index', columns=freq_step)
    temp_df = pd.DataFrame({'Mean' : RT_df.mean(axis=0),
                            'StdDev' : RT_df.std(axis=0)})
    final_df = RT_df.append(temp_df.transpose())
    return final_df
