import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import os
import pandas as pd
# from runReverberationTimeTests import test1
from runReverberationTimeTests import performMeasurement
from calculateReverberationTimes import performRTcalculation

# Take parameters from GUI and start measurement
def triggerMeasurements(n_runs, decay_time, noise_color):
    decay_results = performMeasurement(n_runs, decay_time=decay_time, noise_color=noise_color)
    print('Measurement completed with {} runs'.format(n_runs))
    print('Decay of {} seconds'.format(decay_time))
    print('Noise color: {}'.format(noise_color))
    return decay_results

# Take results from measurements and perform RT calculations
def triggerRTcalc(decay_results, db_decay, decay_time):
    reverberationTimes = performRTcalculation(data=decay_results, db_decay=db_decay, decay_time=decay_time)
    print("Reverb time calculated")
    print(reverberationTimes)
    return reverberationTimes

def save_data(e1_df, e2_df, r1_df, r2_df, env_df, filename):
    print('Creating file and storing data')
    with open(filename, 'w') as f:
        e1_df.to_csv(f)
    with open(filename, 'a') as f:
        if type(e2_df) is not list and e2_df is not None:
            e2_df.to_csv(f)
        if type(r1_df) is not list and  r1_df is not None:
            r1_df.to_csv(f)
        if type(r2_df) is not list and r2_df is not None:
            r2_df.to_csv(f)
        if type(env_df) is not list and env_df is not None:
            env_df.to_csv(f)
    return 1

# Function to assemble RH. temp, and pressure dataframe for storage
def buildRH_TempDF(empty1_RH, empty1_T, empty1_P, empty2_RH, empty2_T, empty2_P, sample1_RH, sample1_T, sample1_P, sample2_RH, sample2_T, sample2_P):
    data = [[empty1_RH, empty1_T, empty1_P],[empty2_RH, empty2_T, empty2_P],[sample1_RH, sample1_T, sample1_P],[sample2_RH, sample2_T, sample2_P]]
    env_df = pd.DataFrame(data, index=['empty1', 'empty2', 'sample1', 'sample2'], columns=['% RH', 'Temp degC', 'Pressure (kPa)'])
    return env_df

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.emptydata1 = []
        self.emptydata2 = []
        self.sampledata1 = []
        self.sampledata2 = []
        self.entry_string1 = ''

        # Setup window and geometry
        parent.geometry("1000x500")
        parent.resizable(0, 0)
        parent.title("Absorption measurement tool")

        # Header
        tk.Label(parent, text="Simple tool for performing sound absorption tests", font=(None, 12)).grid(row=0, column=0, columnspan=7)

        # Entry for number of runs
        tk.Label(parent, text="Number of runs (suggested: 9)").grid(row=1, column=0, columnspan=1)
        self.entryText1 = tk.StringVar()
        self.e1 = tk.Entry(parent, textvariable=self.entryText1)
        self.entryText1.set( "9" )
        self.e1.grid(row=1, column=1, columnspan=1)

        # Entry for decay time
        tk.Label(parent, text="Decay time - seconds").grid(row=1, column=2, columnspan=1)
        self.entryText2 = tk.StringVar()
        self.e2 = tk.Entry(parent, textvariable=self.entryText2)
        self.entryText2.set( "5" )
        self.e2.grid(row=1, column=3, columnspan=1)

        # White or Pink Noise
        self.n_color = tk.StringVar()
        self.n_color.set('pink')
        self.dropdown1 = tk.OptionMenu(parent, self.n_color, "pink", "white")
        self.dropdown1.grid(row=1, column=4, columnspan=1)

        # T20 or T30
        self.rt_db = tk.StringVar()
        self.rt_db.set('t20')
        self.dropdown2 = tk.OptionMenu(parent, self.rt_db, "t20", "t30", "max")
        self.dropdown2.grid(row=1, column=5, columnspan=1)

        ttk.Separator(parent).grid(column=0, row=2, columnspan=7, sticky='ew', pady=10)
        # Empty room measurements
        tk.Label(parent, text="Empty room measurements", font=(None, 12)).grid(row=3, column=0, columnspan=7)
        # Empty room - location 1
        self.empty1_button = tk.Button(parent, text="Speaker Location 1 - Start", command=self.empty1)
        self.empty1_button.grid(row=4, column=0, padx=10, pady=10, columnspan=1)
        self.e1stat = tk.StringVar()
        self.empty1_status = tk.Entry(parent, state='disabled', textvariable=self.e1stat)
        self.empty1_status.grid(row=4, column=1, columnspan=1)
        self.e1stat.set('No data')
        tk.Label(parent, text="%RH").grid(row=5, column=0)
        self.empty1_rh = tk.Entry(parent)
        self.empty1_rh.grid(row=6, column=0)
        tk.Label(parent, text="Temp").grid(row=5, column=1)
        self.empty1_temp = tk.Entry(parent)
        self.empty1_temp.grid(row=6, column=1)
        tk.Label(parent, text="Pressure (kPa)").grid(row=5, column=2)
        self.empty1_press = tk.Entry(parent)
        self.empty1_press.grid(row=6, column=2)

        ttk.Separator(parent, orient=tk.VERTICAL).grid(column=3, row=4, rowspan=3, sticky='ns', padx=5)

        # Empty room - location 2
        self.empty2_button = tk.Button(parent, text="Speaker Location 2 - Start", command=self.empty2)
        self.empty2_button.grid(row=4, column=4, padx=10, pady=10, columnspan=1)
        self.e2stat = tk.StringVar()
        self.empty2_status = tk.Entry(parent, state='disabled', textvariable=self.e2stat)
        self.empty2_status.grid(row=4, column=5, columnspan=1)
        self.e2stat.set('No data')
        tk.Label(parent, text="%RH").grid(row=5, column=4)
        self.empty2_rh = tk.Entry(parent)
        self.empty2_rh.grid(row=6, column=4)
        tk.Label(parent, text="%Temp").grid(row=5, column=5)
        self.empty2_temp = tk.Entry(parent)
        self.empty2_temp.grid(row=6, column=5)
        tk.Label(parent, text="Pressure (kPa)").grid(row=5, column=6)
        self.empty2_press = tk.Entry(parent)
        self.empty2_press.grid(row=6, column=6)

        ttk.Separator(parent).grid(column=0, row=7, columnspan=7, sticky='ew', pady=10)
        # Sample measurements
        tk.Label(parent, text="Sample measurements", font=(None, 12)).grid(row=8, column=0, columnspan=7)
        # Sample - location 1
        self.sample1_button = tk.Button(parent, text="Speaker Location 1 - Start", command=self.sample1)
        self.sample1_button.grid(row=9, column=0, padx=10, pady=10, columnspan=1)
        self.s1stat = tk.StringVar()
        self.sample1_status = tk.Entry(parent, state='disabled', textvariable=self.s1stat)
        self.sample1_status.grid(row=9, column=1, columnspan=1)
        self.s1stat.set('No data')
        tk.Label(parent, text="%RH").grid(row=10, column=0)
        self.sample1_rh = tk.Entry(parent)
        self.sample1_rh.grid(row=11, column=0)
        tk.Label(parent, text="%RH").grid(row=10, column=1)
        self.sample1_temp = tk.Entry(parent)
        self.sample1_temp.grid(row=11, column=1)
        tk.Label(parent, text="Pressure (kPa)").grid(row=10, column=2)
        self.sample1_press = tk.Entry(parent)
        self.sample1_press.grid(row=11, column=2)

        ttk.Separator(parent, orient=tk.VERTICAL).grid(column=3, row=9, rowspan=3, sticky='ns', padx=5)

        # Sample - location 2
        self.sample2_button = tk.Button(parent, text="Speaker Location 2 - Start", command=self.sample2)
        self.sample2_button.grid(row=9, column=4, padx=10, pady=10, columnspan=1)
        self.s2stat = tk.StringVar()
        self.sample2_status = tk.Entry(parent, state='disabled', textvariable=self.s2stat)
        self.sample2_status.grid(row=9, column=5, columnspan=1)
        self.s2stat.set('No data')
        tk.Label(parent, text="%RH").grid(row=10, column=4)
        self.sample2_rh = tk.Entry(parent)
        self.sample2_rh.grid(row=11, column=4)
        tk.Label(parent, text="%RH").grid(row=10, column=5)
        self.sample2_temp = tk.Entry(parent)
        self.sample2_temp.grid(row=11, column=5)
        tk.Label(parent, text="Pressure (kPa)").grid(row=10, column=6)
        self.sample2_press = tk.Entry(parent)
        self.sample2_press.grid(row=11, column=6)

        ttk.Separator(parent).grid(column=0, row=12, columnspan=7, sticky='ew', pady=10)
        # General utilities
        # Save data
        self.save_data_button = tk.Button(parent, text="Save data", command=self.save_data)
        self.save_data_button.grid(row=13, column=0, padx=10, pady=10, columnspan=1)

        ## Reset measurement
        self.reset_button = tk.Button(parent, text="Reset measurement", command=self.reset_measurement)
        self.reset_button.grid(row=14, column=0, padx=10, pady=10, columnspan=1)

        # Display text in GUI
        self.display_text = tk.Text(parent, width=50, height=5)
        self.display_text.grid(row=13, column=4, columnspan=3)

    # Function to perform measurement 1 with empty room
    def empty1(self, event=''):
        print("Empty 1 button pressed")
        self.display_text.insert('1.0', 'Starting empty room - 1 \n')
        N = int(self.e1.get())
        dt = float(self.e2.get())
        nc = str(self.n_color.get())
        db_decay = str(self.rt_db.get())
        self.display_text.insert('1.0', 'Number of runs: {} \n'.format(N))
        self.display_text.insert('1.0', 'Decay time: {} \n'.format(dt))
        self.display_text.insert('1.0', 'Noise color: {} \n'.format(nc))
        decay_results = triggerMeasurements(n_runs=N, decay_time=dt, noise_color=nc)
        self.display_text.insert('1.0', 'Measurement completed - calculating reverb times \n')
        self.emptydata1 = triggerRTcalc(decay_results=decay_results, db_decay=db_decay, decay_time=dt)
        self.display_text.insert('1.0', 'Reverb time calculation completed \n')
        self.e1stat.set('Data')

    # Function to perform measurement 2 with empty room
    def empty2(self, event=''):
        print("Empty 2 button pressed")
        self.display_text.insert('1.0', 'Starting empty room - 2 \n')
        N = int(self.e1.get())
        dt = float(self.e2.get())
        nc = str(self.n_color.get())
        db_decay = str(self.rt_db.get())
        self.display_text.insert('1.0', 'Number of runs: {} \n'.format(N))
        self.display_text.insert('1.0', 'Decay time: {} \n'.format(dt))
        self.display_text.insert('1.0', 'Noise color: {} \n'.format(nc))
        decay_results = triggerMeasurements(n_runs=N, decay_time=dt, noise_color=nc)
        self.display_text.insert('1.0', 'Measurement completed - calculating reverb times \n')
        self.emptydata2 = triggerRTcalc(decay_results=decay_results, db_decay=db_decay, decay_time=dt)
        self.display_text.insert('1.0', 'Reverb time calculation completed \n')
        self.e2stat.set('Data')

    # Function to perform measurement 1 with sample in room
    def sample1(self, event=''):
        print("Sample 1 button pressed")
        self.display_text.insert('1.0', 'Starting sample - 1 \n')
        N = int(self.e1.get())
        dt = float(self.e2.get())
        nc = str(self.n_color.get())
        db_decay = str(self.rt_db.get())
        self.display_text.insert('1.0', 'Number of runs: {} \n'.format(N))
        self.display_text.insert('1.0', 'Decay time: {} \n'.format(dt))
        self.display_text.insert('1.0', 'Noise color: {} \n'.format(nc))
        decay_results = triggerMeasurements(n_runs=N, decay_time=dt, noise_color=nc)
        self.display_text.insert('1.0', 'Measurement completed - calculating reverb times \n')
        self.sampledata1 = triggerRTcalc(decay_results=decay_results, db_decay=db_decay, decay_time=dt)
        self.display_text.insert('1.0', 'Reverb time calculation completed \n')
        self.s1stat.set('Data')

    # Function to perform measurement 2 with sample in room
    def sample2(self, event=''):
        print("Sample 2 button pressed")
        self.display_text.insert('1.0', 'Starting sample - 2 \n')
        N = int(self.e1.get())
        dt = float(self.e2.get())
        nc = str(self.n_color.get())
        db_decay = str(self.rt_db.get())
        self.display_text.insert('1.0', 'Number of runs: {} \n'.format(N))
        self.display_text.insert('1.0', 'Decay time: {} \n'.format(dt))
        self.display_text.insert('1.0', 'Noise color: {} \n'.format(nc))
        decay_results = triggerMeasurements(n_runs=N, decay_time=dt, noise_color=nc)
        self.display_text.insert('1.0', 'Measurement completed - calculating reverb times \n')
        self.sampledata2 = triggerRTcalc(decay_results=decay_results, db_decay=db_decay, decay_time=dt)
        self.display_text.insert('1.0', 'Reverb time calculation completed \n')
        self.s2stat.set('Data')

    # Function to build dataframe, prompt for csv location, and save all data
    def save_data(self, event=''):
        print("Save data button pressed")
        env_df = buildRH_TempDF(empty1_RH=self.empty1_rh.get(), empty1_T=self.empty1_temp.get(), empty1_P=self.empty1_press.get(),
                                empty2_RH=self.empty2_rh.get(), empty2_T=self.empty2_temp.get(), empty2_P=self.empty2_press.get(),
                                sample1_RH=self.sample1_rh.get(), sample1_T=self.sample1_temp.get(), sample1_P=self.sample1_press.get(),
                                sample2_RH=self.sample2_rh.get(), sample2_T=self.sample2_temp.get(), sample2_P=self.sample2_press.get())
        print(env_df)
        save_filename = filedialog.asksaveasfilename(parent=self.parent, initialdir=r'D://', title='Save data as', filetypes=(('csv file', '*.csv'),))
        self.display_text.insert('1.0', 'Saving data in {} \n'.format(save_filename))
        save_data(e1_df=self.emptydata1, e2_df=self.emptydata2, r1_df=self.sampledata1, r2_df=self.sampledata2, env_df=env_df, filename=save_filename)
        self.display_text.insert('1.0', 'Data saved \n')

    # Function to reset all dataframes to allow measurement to be reset
    def reset_measurement(self, event=''):
        self.emptydata1 = []
        self.emptydata2 = []
        self.sampledata1 = []
        self.sampledata2 = []
        self.e1stat.set('No data')
        self.e2stat.set('No data')
        self.s1stat.set('No data')
        self.s2stat.set('No data')

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()

