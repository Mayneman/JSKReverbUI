## Set of functions to perform calculations of variables described in ISO9619-1

from scipy import signal
from scipy.fftpack import fft, fftshift
import numpy as np
import math
import scipy.fftpack
import pandas

class reference_values:
    Pr = 101.325 # Reference atmospheric pressure (kPa)
    T0 = 293.15 # Reference temp (K)
    P0 = 20*10**-6 # Reference sound pressure level (Pa)
    T01 = 273.16 # Triple-point isoltherm temperature (K)

def degCtoK(degC):
    return degC + 273.15


def ktodegC(K):
    return K - 273.15

def pureToneAttenuation(alpha_pure, distance, pi):
    pf = pi*math.exp(-0.1151*alpha_pure*distance)
    att = 10*math.log10((pi**2)/(pf**2))
    return pf, att

def oxygenRelaxationFrequency(hr, Pa, T, Pr=reference_values.Pr):
    # hr = Relative humidity
    # Pa = Atmospheric pressure at time of measurement
    # Pr = Reference atmospheric pressure
    h = molarConc(hr=hr, Pa=Pa, T=T, Pr=reference_values.Pr)
    return (Pa/Pr)*(24+(4.04*10**4)*h*(0.02+h)/(0.391+h))

def nitrogenRelaxationFrequency(hr, Pa, T, T0=reference_values.T0, Pr=reference_values.Pr):
    # hr = Relative humidity
    # Pa = Atmospheric pressure at time of measurement
    # Pr = Reference atmospheric pressure
    # T = Temperature at time of measurement (K)
    # T0 = Reference temp (K)
    h = molarConc(hr=hr, Pa=Pa, T=T, Pr=reference_values.Pr)
    return (Pa/Pr)*((T/T0)**(-0.5))*(9+280*h*math.exp(-4.170*(((T/T0)**(-1/3))-1)))

def molarConc(hr, Pa, T, Pr=reference_values.Pr):
    C = -6.8346*((reference_values.T01/T)**1.261)+4.6151
    Psat = Pr*10**C
    h = hr*(Psat/Pr)/(Pa/Pr)
    return h

def AtmosphericAttenuation(f, hr, Pa, T, Pr=reference_values.Pr, P0=reference_values.P0, T0 = reference_values.T0):
    frO = oxygenRelaxationFrequency(hr=hr, Pa=Pa, T=T)
    frN = nitrogenRelaxationFrequency(hr=hr, Pa=Pa, T=T)
    _1a = 8.686*f**2
    _1b = 1.84*(10**-11)*((Pa/Pr)**-1)*((T/T0)**0.5)
    _2 = (T/T0)**(-5/2)
    _3a = 0.01275*(math.exp(-2239.1/T))
    _3b = (frO+((f**2)/frO))**-1
    _4a = 0.1068*(math.exp(-3352.0/T))
    _4b = (frN+(f**2)/frN)**-1
    # print('1a: {}'.format(_1a))
    # print('1b: {}'.format(_1b))
    # print('2: {}'.format(_2))
    # print('3a: {}'.format(_3a))
    # print('3b: {}'.format(_3b))
    # print('4a: {}'.format(_4a))
    # print('4b: {}'.format(_4b))
    return _1a*(_1b+_2*(_3a*_3b+_4a*_4b))

def powerAttenuationFactor(alpha):
    return alpha/(10*math.log10(math.exp(1)))

def speedOfSound(T, T0=reference_values.T0):
    return 343.2*((T/T0)**0.5)