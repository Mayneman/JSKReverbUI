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
# sys.path.insert(1, r"D:\Scripts\standards\standards") # Scrum PC
sys.path.insert(1, r"D:\ReverberationRoom\standards\standards") # Rob PC
import filterAndBands
import helpers
import iso354

# import standard for calculation of absorption area

## Put a 'try' in this to return RT =0 rather than crashing

# (V=volume, RT=rt, T=temp, f=int(freq), hr=relativeHumidity, Pa=pressure*1000))

def performRTcalculation(data, volume, temp, relativeHumidity, pressure, db_decay='t20', decay_time=5):
    # Set path to configuration file - needs to be absolute for executable
    # config_data = helpers.parseConfigFile(path=r'D:\Scripts\reverb-tkinter-interface\config.cfg')
    config_data = helpers.parseConfigFile(path=r'D:\ReverberationRoom\tkinter-interface\config.cfg')
    # Read all configuration data
    print('Reading config data from .config file')
    fs = int(config_data['samplingfrequency'])
    rise_time = float(config_data['risetime'])
    excitation_time = float(config_data['excitationtime'])
    mics = config_data['micid']
    channel_name = config_data['micnames']
    analog_output_id = config_data['outputid']
    estRT = float(config_data['estimatedrt'])
    pRef = float(config_data['referencepressure'])
    p_ref = pRef
    n_mics = int(config_data['nummics'])
    window_time = float(config_data['windowtime'])
    fLow = int(config_data['flow'])
    fHigh = int(config_data['fhigh'])
    averaging_type = config_data['avgtype']
    signal_type = config_data['usestoredexcitation']
    
    # General parameters
    t_tot = rise_time+excitation_time+decay_time
    N_samp = int(t_tot)*fs
    dt = 1.0/fs
    t_array = np.arange(start=0, stop=t_tot, step=dt)
    wT = estRT/48
    windowN=int(wT*fs)
    window_length = windowN
    print("Length of window: {}s : {} samples".format(window_time, windowN))
    total_reverb = {}
    mic_location = [1, 2, 3, 4, 5, 6]

    # Perform ensemble averaging of individual mics for number of runs
    # averaged_data = helpers.ensemble_average(raw_data=data, n_mics=n_mics)
    print('Performing ensemble averaging at each microphone')
    mean_data = np.mean(a=data, axis=0)

    # Build pandas df for data
    print('Inserting data into pandas dataFrame')
    df = pd.DataFrame()
    rt_df = pd.DataFrame(columns=['frequency_Hz']+mics)
    for row, mic in zip(mean_data, mics):
        print('Inserted mic: {}'.format(mic))
        df['mean_{}'.format(mic)] = row

    # Step though mics and calculate RT
    for mic in mics:
        print('Calculating RT for mic: {}'.format(mic))
        # Perform 3rd octave filters
        print('Applying 1/3rd Octave filters to data between {}Hz - {}Hz'.format(fLow, fHigh))
        filtered_data = filterAndBands.thirdOctFilters(data=df['mean_{}'.format(mic)], fs=fs, f_low=fLow, f_high=fHigh)
        rt_df['frequency_Hz'] = filtered_data.keys()
        for key in filtered_data:
            df['{}_{}Hz'.format(mic, key)] = 10*np.log10((abs(filtered_data[key])**2)/(p_ref**2))
        # df['{}_log_data'.format(mic)] = 10*np.log10(abs(df['mean_{}'.format(mic)])/p_ref)
        df['{}_samples'.format(mic)] = np.arange(len(df['mean_{}'.format(mic)]))
        df['{}_seconds'.format(mic)] = df['{}_samples'.format(mic)]/fs
        dummy_RT = []
        for key in filtered_data:
            print("Averaging {}Hz band for {}".format(key, mic))
            df['{}_{}Hz_exp'.format(mic, key)] = df['{}_{}Hz'.format(mic,key)].ewm(span=window_length, adjust=False).mean()
            # df['{}_{}Hz_lin'.format(mic, key)] = df['{}_{}Hz'.format(mic,key)].rolling(window=window_length).mean()
            windowed_data = df['{}_{}Hz_{}'.format(mic, key, averaging_type)].values
            t_array = df['{}_seconds'.format(mic)].values
            
            print('Seperating signal into sections for evaluation')
            excitation_range = [int((rise_time)*fs), int((rise_time+excitation_time)*fs)]
            excitation_level = filterAndBands.dBavg(windowed_data[excitation_range[0]+int(0.5*fs):excitation_range[1]-int(0.5*fs)])
            trigger_level = excitation_level - 5
            print('Excitation - 5dB: {}'.format(trigger_level))
            min_decay_level = min(windowed_data[excitation_range[1]:])
            bg_start = len(windowed_data) - 2*fs
            bg_level = filterAndBands.dBavg(windowed_data[bg_start:])
            if db_decay == 't20':
                bg_trigger_level = max([trigger_level - 20, bg_level+5])
                print('Trigger level - 20dB: {}'.format(bg_trigger_level))
            elif db_decay == 't30':
                bg_trigger_level = max([trigger_level - 30, bg_level+5])
                print('Trigger level - 30dB: {}'.format(bg_trigger_level))
            elif db_decay == 'all':
                bg_trigger_level = bg_level + 10
                print('Background + 10dB: {}'.format(bg_trigger_level))
            ndx_start = np.where(windowed_data[excitation_range[1]:] <= trigger_level)
            decay_start = ndx_start[0][0]
            print('Start of evaluation range {} seconds'.format(decay_start, decay_start/fs))
            ndx_end = np.where(windowed_data[excitation_range[1]:] <= bg_trigger_level)
            decay_end = ndx_end[0][0]
            print('End of evaluation range {} samples / {} seconds'.format(decay_end, decay_end/fs))

            print("Calculating RT of {}Hz band for {}".format(key, mic))
            fitting_level = windowed_data[excitation_range[1]+decay_start:excitation_range[1]+decay_end]
            fitting_times = t_array[excitation_range[1]+decay_start:excitation_range[1]+decay_end]
            slope, intercept, r_value, p_value, std_err = stats.linregress(x=fitting_times,y=fitting_level)
            print('Slope: {}, intercept: {}, R-squared: {}'.format(slope, intercept, r_value))
            t_plot = np.arange(start=0, stop=rise_time+excitation_time+decay_time, step=0.1)
            y_fitted = slope*t_plot + intercept
            print("R-squared: {}".format(r_value))
            RT = -60/slope
            dummy_RT.append(RT)
            print("Reverberation Time at {} Hz: {}s".format(key, RT))

        rt_df[mic] = dummy_RT
    
    print('Reverb time prior to averaging')
    print(rt_df)
    rt_df = rt_df.set_index('frequency_Hz')
    rt_df['avg'] = rt_df.mean(axis=1)
    print('Averaged RT')
    print(rt_df)
    print('Calculating Absorption Area')
    a = []
    for freq in rt_df.index.array:
        print('Calculating absorption area for {} Hz'.format(freq))
        rt = rt_df.loc[freq]
        print(rt)
        rt = rt['avg']
        print('Average RT: {}'.format(rt))
        a.append(iso354.soundAbsorptionArea(V=volume, RT=rt, T=temp, f=int(freq), hr=relativeHumidity, Pa=pressure*1000))
    rt_df['abs_area'] = a

    return rt_df
