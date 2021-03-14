import json
import os
import random
import numpy as np
import scipy
from numpy.fft import irfft
import nidaqmx
from nidaqmx.constants import AcquisitionType
import configparser
from time import sleep

import helpers

def performMeasurement(n_runs, decay_time, noise_color):
    # Read configuration file - needs to be absolute path for exe file
    config_data = helpers.parseConfigFile(path=r'D:\Scripts\reverb-tkinter-interface\config.cfg')
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
    # Generate excitation array
    excitation_array, t_array = helpers.createExcitation(rise_time=rise_time, excitation_time=excitation_time, decay_time=decay_time, fs=fs, noise_color=noise_color)
    t_tot = rise_time+excitation_time+decay_time
    N_samp = int(t_tot)*fs
    # Setup NI task
    with nidaqmx.task.Task("OutputTask") as ao_task, nidaqmx.task.Task('InputTask') as ai_task:
        print("Setting up generator")
        ################## Setup analogue output ################
        ao_chan_name = ao_device_name+'/'+analog_output_id
        print('AO channel name: {}'.format(ao_chan_name))
        ao_task.ao_channels.add_ao_voltage_chan(ao_chan_name,
                                                name_to_assign_to_channel='speaker_output',
                                                min_val=-3.0,
                                                max_val=3.0)
        ao_task.timing.cfg_samp_clk_timing(fs,
                                        sample_mode=AcquisitionType.FINITE,
                                        samps_per_chan=N_samp)
        ao_task.write(excitation_array,
                auto_start=False)
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
        results = []
        print("Starting measurements")
        for nxd in range(n_runs):
            print("Run: {}".format(nxd))
            # Start output signal and measurement
            ao_task.start()
            ai_task.start()
            # Wait until both tasks are complete
            ao_task.wait_until_done(timeout=t_tot+5)
            ai_task.wait_until_done(timeout=t_tot+5)
            # Record data from mic
            data = ai_task.read(number_of_samples_per_channel=N_samp)
            # Stop both tasks
            ao_task.stop()
            ai_task.stop()
            results.append(data)
        print("Measurement completed")
        results_np = np.array(results)
        print(results_np)
        return results_np


def test1():
    print("Starting delay")
    sleep(10)
    print("Delay done")
