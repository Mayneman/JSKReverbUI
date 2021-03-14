""" This script provides a user interface for the JSK Acoustics Reverberation Room
Author: Robin Wareing - Altissimo Consulting Ltd. - altissimo.nz - rob@altissimo.nz

Utilises the NI-DAQmx driver set and the nidaqmx python interface to trigger measurements in the reverberation room

Uses methodology specified in ISO 354 to perform absorption measurements.


"""

## General imports
# Tkinter for GUI construction
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
# Pandas for storing incoming data in DataFrames
import pandas as pd
# Numpy is used to store raw data as this is the most space efficient
import numpy as np
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

# Function to assemble RH. temp, and pressure dataframe for storage
def buildRH_TempDF(meas1_RH, meas1_T, meas1_P):
    data = [[meas1_RH, meas1_T, meas1_P]]
    env_df = pd.DataFrame(data, index=['meas1'], columns=['% RH', 'Temp degC', 'Pressure (kPa)'])
    return env_df

# This is the main function that defines the layout of the GUI
# The gui items are defined using a static grid
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data1 = []
        self.entry_string1 = ''
        self.decay_results = []

        # Setup window and geometry
        parent.geometry("800x500")
        parent.resizable(0, 0)
        parent.title("Single reverb time test")

        # Header
        tk.Label(parent, text="Tool for performing a single reverb time test", font=(None, 12)).grid(row=0, column=0, columnspan=7)

        # Entry for number of runs
        tk.Label(parent, text="Number of runs (suggested: 9)").grid(row=1, column=0, columnspan=1)
        self.entryText1 = tk.StringVar()
        self.e1 = tk.Entry(parent, textvariable=self.entryText1)
        self.entryText1.set( "9" )
        self.e1.grid(row=1, column=1, columnspan=1)

        # Entry for decay time
        tk.Label(parent, text="Decay time - seconds").grid(row=2, column=0, columnspan=1)
        self.entryText2 = tk.StringVar()
        self.e2 = tk.Entry(parent, textvariable=self.entryText2)
        self.entryText2.set( "8" )
        self.e2.grid(row=2, column=1, columnspan=1)

        # White or Pink Noise
        self.n_color = tk.StringVar()
        self.n_color.set('pink')
        self.dropdown1 = tk.OptionMenu(parent, self.n_color, "pink", "white")
        self.dropdown1.grid(row=1, column=2, columnspan=1)

        # T20 or T30
        self.rt_db = tk.StringVar()
        self.rt_db.set('t30')
        self.dropdown2 = tk.OptionMenu(parent, self.rt_db, "t20", "t30", "max")
        self.dropdown2.grid(row=2, column=2, columnspan=1)

        # Entry for room volume
        tk.Label(parent, text="Room Volume").grid(row=1, column=3, columnspan=1)
        self.roomVol = tk.StringVar()
        self.rVol = tk.Entry(parent, textvariable=self.roomVol)
        self.roomVol.set( "219" )
        self.rVol.grid(row=1, column=4, columnspan=1)

        # Select to save data
        tk.Label(parent, text="Save Raw Data").grid(row=2, column=3, columnspan=1)
        self.sv_raw = tk.StringVar()
        self.sv_raw.set('yes')
        self.save_raw = tk.OptionMenu(parent, self.sv_raw, "yes", "no")
        self.save_raw.grid(row=2, column=4, columnspan=1)

        # Measurement controls
        ttk.Separator(parent).grid(column=0, row=3, columnspan=7, sticky='ew', pady=10)
        tk.Label(parent, text='Run measurement', font=(None, 12)).grid(row=4, column=0, columnspan=7)
        self.meas1_button = tk.Button(parent, text="Start - measurements", command=self.meas1)
        self.meas1_button.grid(row=5, column=0, padx=10, pady=10, columnspan=1)
        self.e1stat = tk.StringVar()
        self.meas1_status = tk.Entry(parent, state='disabled', textvariable=self.e1stat)
        self.meas1_status.grid(row=5, column=1, columnspan=1)
        self.e1stat.set('No data')

        ## Environmental parameters
        ttk.Separator(parent).grid(column=0, row=6, columnspan=7, sticky='ew', pady=10)
        tk.Label(parent, text='Environmental', font=(None, 12)).grid(row=7, column=0, columnspan=7)
        # Temp
        tk.Label(parent, text="Temp").grid(row=8, column=0)
        self.e1T = tk.StringVar()
        self.meas1_temp = tk.Entry(parent, textvariable=self.e1T)
        self.e1T.set( "25" )
        self.meas1_temp.grid(row=9, column=0)
        # Humidity
        tk.Label(parent, text="%RH").grid(row=8, column=1)
        self.e1RH = tk.StringVar()
        self.meas1_rh = tk.Entry(parent, textvariable=self.e1RH)
        self.e1RH.set( "60" )
        self.meas1_rh.grid(row=9, column=1)
        # Pressure
        tk.Label(parent, text="Pressure (kPa)").grid(row=8, column=2)
        self.e1P = tk.StringVar()
        self.meas1_press = tk.Entry(parent, textvariable=self.e1P)
        self.e1P.set( "101" )
        self.meas1_press.grid(row=9, column=2)

        ## Utilities
        ttk.Separator(parent).grid(column=0, row=10, columnspan=7, sticky='ew', pady=10)
        tk.Label(parent, text='Utilities', font=(None, 12)).grid(row=11, column=0, columnspan=7)
        # Save data
        self.save_data_button = tk.Button(parent, text="Save data", command=self.save_data)
        self.save_data_button.grid(row=12, column=0, padx=10, pady=10, columnspan=1)

        ## Reset measurement
        self.reset_button = tk.Button(parent, text="Reset measurement", command=self.reset_measurement)
        self.reset_button.grid(row=13, column=0, padx=10, pady=10, columnspan=1)

        # Set source volume
        tk.Label(parent, text="Volume (0-100)").grid(row=12, column=2)
        self.volP = tk.StringVar()
        self.vol1_val = tk.Entry(parent, textvariable=self.volP)
        self.volP.set( "100" )
        self.vol1_val.grid(row=13, column=2)

    # Function to perform measurement
    def meas1(self, event=''):
        print("Start measurement button pressed")
        N = int(self.e1.get())
        dt = float(self.e2.get())
        nc = str(self.n_color.get())
        db_decay = str(self.rt_db.get())
        volume=float(self.rVol.get())
        temp=float(self.meas1_temp.get())
        relativeHumidity=float(self.meas1_rh.get())
        pressure=float(self.meas1_press.get())
        source_volume = int(self.vol1_val.get())
        print('Number of runs: {} \n Decay time: {} \n Noise color: {} \n'.format(N, dt, nc))
        self.decay_results = triggerMeasurements(n_runs=N, decay_time=dt, noise_color=nc, source_volume=source_volume)
        print('Measurement completed - calculating reverb times')
        # self.data1 = triggerRTcalc(decay_results=decay_results, db_decay=db_decay, decay_time=dt)
        self.data1 = triggerRTcalc(decay_results=self.decay_results, db_decay=db_decay, decay_time=dt, volume=volume, temp=temp, relativeHumidity=relativeHumidity, pressure=pressure)
        print('Reverb time calculation completed')
        self.e1stat.set('Data')

    # Function to build dataframe, prompt for csv location, and save all data
    def save_data(self, event=''):
        saveRaw=str(self.sv_raw.get())
        print("Save data button pressed")
        env_df = buildRH_TempDF(meas1_RH=self.meas1_rh.get(), meas1_T=self.meas1_temp.get(), meas1_P=self.meas1_press.get())
        print(env_df)
        save_filename = filedialog.asksaveasfilename(parent=self.parent, initialdir=r'D://', title='Save data as', filetypes=(('csv file', '*.csv'),))
        print('Saving data in {} \n'.format(save_filename))
        save_data(e1_df=self.data1, env_df=env_df, filename=save_filename)
        print(saveRaw)
        if saveRaw =='yes':
            print('Saving raw data')
            save_raw_data(raw_data=self.decay_results, filename=save_filename)
        print('Data saved \n')

    # Function to reset all dataframes to allow measurement to be reset
    def reset_measurement(self, event=''):
        self.data1 = []
        self.e1stat.set('No data')
        self.decay_results = []
        print('Measurement Reset')

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()

