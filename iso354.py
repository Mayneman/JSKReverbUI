## Set of functions to perform calculations of variables described in ISO 354
from scipy import signal
from scipy.fftpack import fft, fftshift
import numpy as np
import math
import scipy.fftpack
import pandas

import iso9619_1

def soundAbsorptionArea(V, RT, T, f, hr, Pa):
    # print("Reverberation time: {}, Frequency: {}".format(RT, f))
    # print("Temp: {}".format(T))
    alpha = iso9619_1.AtmosphericAttenuation(f=f, hr=hr, Pa=Pa, T=T)
    m = iso9619_1.powerAttenuationFactor(alpha=alpha)
    c = iso9619_1.speedOfSound(T=T, T0=iso9619_1.reference_values.T0)
    A = 55.3*V/(c*RT) - 4*V*m
    return A

def equivalentAbsorptionArea(A1, A2):
    diff = A2 - A1
    return diff

def absorptionCoefficient(AT, S):
    coeff = AT/S
    return coeff

# def practicalSoundAbs(coeff, f):