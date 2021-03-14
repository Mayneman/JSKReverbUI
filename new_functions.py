import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Local import of measurement and calculation scripts
from runReverberationTimeTests import performMeasurement
from calculateReverberationTimes import performRTcalculation

# Take parameters from GUI and start room measurement - this is a blocking action and will preclude use of the front end software during measurements
def triggerMeasurements(n_runs, decay_time, noise_color, source_volume):
    decay_results = performMeasurement(n_runs, decay_time=decay_time, noise_color=noise_color, source_volume=source_volume)
    print('Measurement completed with {} runs'.format(n_runs))
    print('Decay of {} seconds'.format(decay_time))
    print('Noise color: {}'.format(noise_color))
    return decay_results

# Take results from measurements and perform RT calculations according to ISO 354 methodology
def triggerRTcalc(decay_results, db_decay, decay_time, volume, temp, relativeHumidity, pressure):
    reverberationTimes = performRTcalculation(data=decay_results, volume=volume, temp=temp, relativeHumidity=relativeHumidity, pressure=pressure, db_decay=db_decay, decay_time=decay_time)
    print("Reverb time calculated")
    print(reverberationTimes)
    return reverberationTimes

# Store environmental data and calculated reverberation times in a CSV file
def save_data(e1_df, env_df, filename):
    print('Creating file and storing data')
    with open('{}.csv'.format(filename), mode='w') as f:
        e1_df.to_csv(f)
    with open('{}.csv'.format(filename), mode='a') as f:
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

def new_meas1(number_of_runs, decay_time, noise_type, room_volume, room_temp, room_humidity, room_pressure, volume):
    print('Number of runs: {} \nDecay time: {} \nNoise color: {} \n'.format(number_of_runs, decay_time, noise_type))
    decay_results = triggerMeasurements(number_of_runs, decay_time, noise_type, room_volume)
    print('Measurement completed - calculating reverb times')
    data1 = triggerRTcalc(decay_results, decay_time, noise_type, volume,
                               room_temp, room_humidity, room_pressure)
    print('Reverb time calculation completed')
    return data1


# Function to assemble RH. temp, and pressure dataframe for storage
def buildRH_TempDF(meas1_RH, meas1_T, meas1_P):
    data = [[meas1_RH, meas1_T, meas1_P]]
    env_df = pd.DataFrame(data, index=['meas1'], columns=['% RH', 'Temp degC', 'Pressure (kPa)'])
    return env_df


# Save Raw data bool, room humidity, room temp, pressure, data1
def new_save_data(isRaw, rh, room_temperature, pressure, data):
    saveRaw = str(isRaw)
    print("Save data button pressed")
    env_df = buildRH_TempDF(rh, room_temperature, pressure)
    print(env_df)
    # TODO: Make this dynamic through config.
    root = tk.Tk()
    root.withdraw()
    save_filename = filedialog.asksaveasfilename(initialdir=r'D://', title='Save data as', filetypes=(('csv file', '*.csv'),))
    print('Saving data in {} \n'.format(save_filename))
    save_data(data, env_df=env_df, filename=save_filename)
    print(saveRaw)
    # TODO: enable saving of decay results.
    # if saveRaw == 'yes':
    #     print('Saving raw data')
    #     save_raw_data(raw_data=self.decay_results, filename=save_filename)
    # print('Data saved \n')

# Function to reset all dataframes to allow measurement to be reset
def reset_measurement(self, event=''):
    self.data1 = []
    self.e1stat.set('No data')
    self.decay_results = []
    print('Measurement Reset')