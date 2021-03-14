import numpy as np
from scipy import signal

referenceThirdOctaves = [12.5,16,20,25,
                    31.5,40,50,63,
                    80,100,125,160,
                    200,250,315,400,
                    500,630,800,1000,
                    1250,1600,2000,2500,
                    3150,4000,5000,6300,
                    8000,10000,12500,16000,
                    20000]


referenceOctaves = [16,31.5,63,125,
                    250,500,1000,2000,
                    4000,8000,16000]

matches = {16: [12.5,16,20],
           31.5: [25,31.5,40],
           63: [50,63,80],
           125: [100,125,160],
           250: [200,250,315],
           500: [400,500,630],
           1000: [800,1000,1250],
           2000: [1600,2000,2500],
           4000: [3150,4000,5000],
           8000: [6300,8000,10000],
           16000: [12500,16000,20000]}

def BuildThirdOctave(startFreq,stopFreq, referenceThirdOctaves=referenceThirdOctaves):
    thirdOctaves = []
    for band in referenceThirdOctaves:
        if band >= startFreq and band <= stopFreq:
            thirdOctaves.append(band)
    return thirdOctaves

def BuildOctave(startFreq,stopFreq, referenceOctaves=referenceOctaves):
    octaves = []
    for band in referenceOctaves:
        if band >= startFreq and band <= stopFreq:
            octaves.append(band)   
    return octaves

def octToThirdDict(startFreq, stopFreq, matches=matches):
    matchingBands = {}
    for band in matches:
        if band >= startFreq and band <= stopFreq:
            matchingBands[band] = matches[band]
    return matchingBands

def minMaxThirdFreq(centerFreq):
    fd = 2**(1.0/6.0)
    f_min = int(centerFreq/fd)
    f_max = int(centerFreq*fd)
    return f_min, f_max

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low, high], btype='band', output='sos')
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.sosfilt(sos=sos, x=data)
    return y

def thirdOctFilters(data, fs=51200, f_low=50, f_high=5000):
    cf = BuildThirdOctave(startFreq=f_low, stopFreq=f_high, referenceThirdOctaves=referenceThirdOctaves)
    order = 6
    filtered_data = {}
    for freq in cf:
        f_min, f_max = minMaxThirdFreq(centerFreq=freq)
        sos = butter_bandpass(lowcut=f_min, highcut=f_max, fs=fs, order=order)
        y = signal.sosfilt(sos=sos, x=data)
        filtered_data[freq] = y
    return filtered_data

def dBavg(data):
    p_abs = 10**(data/10)
    p_avg = np.mean(p_abs)
    avg = 10*np.log10(p_avg)
    return avg

# def totalBandPower(data, fs=51200, f_low=50, f_high=5000):