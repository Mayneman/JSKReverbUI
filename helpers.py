import json
import os
import random
import numpy as np
import scipy
from numpy.fft import irfft
import configparser
from time import sleep

def parseConfigFile(path):
    config = configparser.ConfigParser()
    config_file = path
    config.read(config_file)
    config_data = {}
    for key in config['DEFAULT']:
        value = config['DEFAULT'][key]
        if ',' in value:
            value_to_store = value.split(',')
        else:
            value_to_store = value
        config_data[key] = value_to_store
    return config_data

def ms(x):
    return (np.abs(x)**2.0).mean()

def normalize(y, x=None):
    if x is not None:
        x = ms(x)
    else:
        x = 1.0
    return y * np.sqrt(x / ms(y))

def generateWhiteNoise(t, fs):
    N = int(t*fs)
    state_white = np.random.RandomState()
    y_white = state_white.randn(N)
    return y_white

def generatePinkNoise(t, fs):
    N = int(t*fs)
    state_pink = np.random.RandomState()
    uneven = N % 2
    X = state_pink.randn(N // 2 + 1 + uneven) + 1j * state_pink.randn(N // 2 + 1 + uneven)
    S = np.sqrt(np.arange(len(X)) + 1.)  # +1 to avoid divide by zero
    y_pink = (irfft(X / S)).real
    y_pink_norm = normalize(y_pink)
    return y_pink_norm

def applyRamp(x, t_rise, fs):
    N_rise = int(t_rise*fs)
    N = len(x)
    ramp = np.linspace(start=0.01, stop=1, num=N_rise)
    ramp = np.pad(ramp, (0,N-N_rise), 'constant', constant_values=1)
    y =  np.multiply(ramp, x)
    return y

def applyDecay(x, t_decay, fs):
    N_decay = int(t_decay*fs)
    y = np.pad(x, (0, N_decay), 'constant', constant_values=0)
    return y

def scaleInput(x, maxL):
    scale = max(abs(x))/abs(maxL)
    y = x*0.9/scale
    return y

def createExcitation(rise_time, excitation_time, decay_time, fs, noise_color="pink"):
    t_in = rise_time+excitation_time
    if noise_color == "pink":
        initial_array = generatePinkNoise(t=t_in, fs=fs)
    elif noise_color == "white":
        initial_array = generateWhiteNoise(t=t_in, fs=fs)
    ramped_excitation = applyRamp(x=initial_array, t_rise=rise_time, fs=fs)
    decay_excitation = applyDecay(x=ramped_excitation, t_decay=decay_time, fs=fs)
    excitation_array = scaleInput(x=decay_excitation, maxL=3)
    N = len(excitation_array)
    t_tot = N/fs
    t_array = np.arange(start=0, stop=len(excitation_array), step=1) * 1.0/fs
    return excitation_array, t_array

def usePreExcitation(rise_time, excitation_time, decay_time, fs, noise_color="pink", signal_num = 1):
    t_in = rise_time+excitation_time
    N = int(t_in*fs)
    if noise_color == "pink":
        # Import pink noise and clip to length
        raw_data = np.load(r'NoiseFiles\pinkNoise{}.npy'.format(signal_num)) # Nick PC
        initial_array = raw_data[:N]
    elif noise_color == "white":
        # Import white noise and clip to length
        raw_data = np.load(r'NoiseFiles\whiteNoise{}.npy'.format(signal_num)) # Nick PC
        initial_array = raw_data[:N]
    ramped_excitation = applyRamp(x=initial_array, t_rise=rise_time, fs=fs)
    decay_excitation = applyDecay(x=ramped_excitation, t_decay=decay_time, fs=fs)
    excitation_array = scaleInput(x=decay_excitation, maxL=3)
    N = len(excitation_array)
    t_tot = N/fs
    t_array = np.arange(start=0, stop=len(excitation_array), step=1) * 1.0/fs
    return excitation_array, t_array

def ensemble_average(raw_data, n_mics):
    ensembleAveraged = []
    for ndx in np.arange(n_mics):
        dataToAvg = raw_data[:, ndx, :]
        dataToAvg_PA = np.power(10, dataToAvg/10)
        avgPA = np.mean(dataToAvg_PA, axis=0)
        ensembleAveraged.append(10*np.log10(avgPA))

    return ensembleAveraged

def moving_average(x, n=3):
    ret = np.cumsum(x)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
