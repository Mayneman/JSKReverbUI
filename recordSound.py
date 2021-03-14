import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import pandas as pd
import numpy as np

import nidaqmx
from nidaqmx.constants import AcquisitionType

import helpers




# config_data = helpers.parseConfigFile(path=r'D:\Scripts\reverb-tkinter-interface\config.cfg') # Rob PC
config_data = helpers.parseConfigFile(path=r'D:\Scripts\reverb-tkinter-interface\config.cfg') # Scrum PC
ao_device_name = config_data['aodevicename']
ai_device_name = config_data['aidevicename']
dio_device_name = config_data['diodevicename']
fs = int(config_data['samplingfrequency'])
# decay_time = float(config_data['decaytime'])
mics = config_data['micid']
channel_name = config_data['micnames']

t_tot = 1200
N_samp = int(t_tot)*fs
n_runs = 1
ndx = 3

with nidaqmx.task.Task('InputTask') as ai_task:
    ############ Setup microphone inputs #############
    print("Setting up inputs")
    for micID, channel in zip(mics, channel_name):
        ai_chan_name = ai_device_name+'/'+micID
        print('AI channel name: {}'.format(ai_chan_name))
        ai_task.ai_channels.add_ai_microphone_chan(ai_chan_name,
                                                name_to_assign_to_channel=channel,
                                                mic_sensitivity=22.4,
                                                max_snd_press_level=140,
                                                units=nidaqmx.constants.SoundPressureUnits.PA)
    ai_task.timing.cfg_samp_clk_timing(fs,
                                    sample_mode=AcquisitionType.FINITE,
                                    samps_per_chan=N_samp)
    # for ndx in range(n_runs):
    print("Start measurement: {}".format(ndx))
    ai_task.start()
    # Wait until task is complete
    ai_task.wait_until_done(timeout=t_tot+5)
    print("measurement completed")
    # Record data from mic
    data = ai_task.read(number_of_samples_per_channel=N_samp)
    # Stop both tasks
    ai_task.stop()
    print("stopping measurement")
    results = np.array(data)
    print(results)
    filename = 'testData/backgroundMeasurement_{}'.format(ndx)
    np.save(filename, results)