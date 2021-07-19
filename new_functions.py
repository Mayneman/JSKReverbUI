import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import plotly.graph_objects as go
import dash_core_components as dcc

# Local import of measurement and calculation scripts
import logger
from runReverberationTimeTests import performMeasurement
from calculateReverberationTimes import performRTcalculation


# Take parameters from GUI and start room measurement - this is a blocking action and will preclude use of the front end software during measurements
def triggerMeasurements(n_runs, decay_time, noise_color, source_volume):
    decay_results = performMeasurement(n_runs, decay_time=decay_time, noise_color=noise_color, source_volume=source_volume)
    print('Measurement completed with {} runs'.format(n_runs))
    logger.add_text('Measurement completed with {} runs'.format(n_runs))
    print('Decay of {} seconds'.format(decay_time))
    print('Noise color: {}'.format(noise_color))
    return decay_results


# Take results from measurements and perform RT calculations according to ISO 354 methodology
def triggerRTcalc(decay_results, decay_time, db_decay, volume, temp, relativeHumidity, pressure):
    reverberationTimes = performRTcalculation(data=decay_results, volume=volume, temp=temp, relativeHumidity=relativeHumidity, pressure=pressure, db_decay=db_decay, decay_time=float(decay_time))
    print("Reverb time calculated")
    print("Reverb time calculated")
    return reverberationTimes


# Store environmental data and calculated reverberation times in a CSV file
def save_data(e1_df, env_df, filename):
    print('Creating file and storing data')
    with open(filename, mode='w') as f:
        e1_df.to_csv(f)
    with open(filename, mode='a') as f:
        if type(env_df) is not list and env_df is not None:
            env_df.to_csv(f)
    return 1


# Store raw measurement data as a npy file for future processing or plotting
def save_raw_data(raw_data, filename):
    print('Storing raw data as .npy file')
    print("Shape of raw data to save: {}".format(np.shape(raw_data)))
    exit()
    np.save(filename, raw_data)
    print('Stored raw data')
    return 1


def new_meas1(number_of_runs, decay_time, noise_type, db_decay, room_temp, room_humidity, room_pressure, volume):
    print('Number of runs: {} \nDecay time: {} \nNoise color: {} \n'.format(number_of_runs, decay_time, noise_type))
    # USE 0-100 HERE
    decay_results = triggerMeasurements(number_of_runs, decay_time, noise_type, 100)
    print('Measurement completed - calculating reverb times')
    # decay_results, db_decay, decay_time, volume, temp, relativeHumidity, pressure
    # USE 219 HERE
    data1 = triggerRTcalc(decay_results, decay_time, db_decay, volume,
                               room_temp, room_humidity, room_pressure)
    print('Reverb time calculation completed')
    return data1


# Function to assemble RH. temp, and pressure dataframe for storage
def buildRH_TempDF(meas1_RH, meas1_T, meas1_P):
    data = [[meas1_RH, meas1_T, meas1_P]]
    env_df = pd.DataFrame(data, index=['meas1'], columns=['% RH', 'Temp degC', 'Pressure (kPa)'])
    return env_df


def save_csv(save_filename, rh, room_temperature, pressure, data):
    env_df = buildRH_TempDF(rh, room_temperature, pressure)
    save_data(data, env_df=env_df, filename=save_filename)
    logger.add_text(save_filename + ' has been created and saved.')
    print(save_filename)
    return


# Save Raw data bool, room humidity, room temp, pressure, data1
def new_save_data(isRaw, rh, room_temperature, pressure, data):
    print("Save data button pressed")
    env_df = buildRH_TempDF(rh, room_temperature, pressure)
    print(env_df)
    #TODO: Fix bug where double click throws async error, fine for now.
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    save_filename = filedialog.askdirectory()
    root.destroy()
    print('root', root)
    root = None
    print('Saving data in {} \n'.format(save_filename))
    # TODO: Save Data .csv change to new function after run.
    # save_data(data, env_df=env_df, filename=save_filename)
    # TODO: enable saving of decay results.
    # if saveRaw == 'yes':
    #     print('Saving raw data')
    #     save_raw_data(raw_data=self.decay_results, filename=save_filename)
    # print('Data saved \n')
    return save_filename

# Function to reset all dataframes to allow measurement to be reset

def reset_measurement(self, event=''):
    self.data1 = []
    self.e1stat.set('No data')
    self.decay_results = []
    print('Measurement Reset')


def log_text(console, message):
    new_value = console + '\n' + message
    return new_value

