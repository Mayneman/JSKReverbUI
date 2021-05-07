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
import logger

def performMeasurement(n_runs, decay_time, noise_color, source_volume):
    # Load configuration file - this needs to be absolute path for exe file
    config_data = helpers.parseConfigFile(path=r'config.cfg') # Nick PC

    ## The system names for the NI devices can be found using the NI-MAX package which is installed as part of the DAQ-mx installation
    ## These names can be changed in NI-MAX, but need to be updated in the software configuration file
    ao_device_name = config_data['aodevicename']    # Name of NI analog output device - 2 channel voltage output
    ai_device_name = config_data['aidevicename']    # Name of NI analog input device - 8 channel voltage (microphone) input
    dio_device_name = config_data['diodevicename']  # Name of NI digital input/output device
    # Measurement parameters in config file
    fs = int(config_data['samplingfrequency'])  # Sampling frequency
    rise_time = float(config_data['risetime'])  # Desired rise time for reverberation time measurements. This prevents sharp clips on sound sources
    excitation_time = float(config_data['excitationtime'])  # Desired excitation time for reverberation time measurements
    mics = config_data['micid']     # IDs for microphones as listed in NI-MAX
    channel_name = config_data['micnames']  # Microphone names
    analog_output_id = config_data['outputid']  # IDs for outputs as listed in NI-MAX
    storedSignal = config_data['usestoredexcitation']   # Defines how to generate signal. If true a prebuilt psuedo-random signal is used, otherwise generates a new signal in code (slower)

    # Generate excitation array - use prebuilt excitation if this is set in config.
    # Typically building a new array is significantly slower and will yeild slightly less repeatable results
    # Both signals are non-correlated for each sound source
    if storedSignal == 'true':
        excitation_array1, t_array = helpers.usePreExcitation(rise_time=rise_time, excitation_time=excitation_time, decay_time=decay_time, fs=fs, noise_color="pink", signal_num = 1)
        excitation_array2, t_array = helpers.usePreExcitation(rise_time=rise_time, excitation_time=excitation_time, decay_time=decay_time, fs=fs, noise_color="pink", signal_num = 2)
    else:
        excitation_array1, t_array = helpers.createExcitation(rise_time=rise_time, excitation_time=excitation_time, decay_time=decay_time, fs=fs, noise_color=noise_color)
        excitation_array2, t_array = helpers.createExcitation(rise_time=rise_time, excitation_time=excitation_time, decay_time=decay_time, fs=fs, noise_color=noise_color) 

    # Build 2d array to excite both sources using 2x analog outputs
    twoChanEx = (source_volume/100)*np.vstack([excitation_array1, excitation_array2])
    # Calculate total measurement duration and corresponding number of samples
    t_tot = rise_time+excitation_time+decay_time
    N_samp = int(t_tot)*fs

    # Setup NI task and begin measurement
    with nidaqmx.task.Task("OutputTask") as ao_task, nidaqmx.task.Task('InputTask') as ai_task:
        print("Setting up generator")
        ################## Setup analogue output ################
        for ao_channel in analog_output_id:
            ao_chan_name = ao_device_name+'/'+ao_channel    # Build channel name based on config details
            print('AO channel name: {}'.format(ao_chan_name))
            # Add an analog output channel
            ao_task.ao_channels.add_ao_voltage_chan(ao_chan_name,
                                                name_to_assign_to_channel=ao_channel,
                                                min_val=-3.0,
                                                max_val=3.0)
        # Setup tast timing - use fixed sample length                                                
        ao_task.timing.cfg_samp_clk_timing(fs,
                                        sample_mode=AcquisitionType.FINITE,
                                        samps_per_chan=N_samp)
        # Store outgoing data on chassis but do not start measurement
        ao_task.write(twoChanEx,
                auto_start=False)
        ############ Setup microphone inputs #############
        print("Setting up inputs")
        for micID, channel in zip(mics, channel_name):
            ai_chan_name = ai_device_name+'/'+micID     # Build channel name based on config details
            print('AI channel name: {}'.format(ai_chan_name))
            # Add an analog input channel
            ai_task.ai_channels.add_ai_microphone_chan(ai_chan_name,
                                                    name_to_assign_to_channel=channel,
                                                    mic_sensitivity=22.4,
                                                    max_snd_press_level=140,
                                                    units=nidaqmx.constants.SoundPressureUnits.PA)
        # Setup tast timing - use fixed sample length  
        ai_task.timing.cfg_samp_clk_timing(fs,
                                        sample_mode=AcquisitionType.FINITE,
                                        samps_per_chan=N_samp)
        results = []
        print("Starting measurements")
        for nxd in range(n_runs):
            print("Run: {}".format(nxd))
            logger.add_text("Run: {}/{}".format(nxd + 1, n_runs))
            # Start output signal and measurement
            ao_task.start()
            ai_task.start()
            # Wait until both tasks are complete
            ao_task.wait_until_done(timeout=t_tot+5)
            ai_task.wait_until_done(timeout=t_tot+5)
            # Record data from mic
            data = ai_task.read(number_of_samples_per_channel=N_samp)
            print('Shape of data: {}'.format(np.shape(data)))
            # Stop both tasks
            ao_task.stop()
            ai_task.stop()
            results.append(data)
        print("Measurement completed")
        print('Shape of results: {}'.format(np.shape(results)))
        # Store results in no array and return this data
        results_np = np.array(results)
        print(results_np)
        return results_np


def test1():
    print("Starting delay")
    sleep(10)
    print("Delay done")
