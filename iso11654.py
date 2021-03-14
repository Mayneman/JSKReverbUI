## Set of functions to perform calculations of single number ratings described in AS ISO 11654-2002
import numpy as np
import math
import pandas as pd

def referenceCurve():
    refCurve = {250: 0.80,
                500: 1.00,
                1000: 1.00,
                2000: 1.00,
                4000: 0.90}
    return refCurve

def calculateWeightedAbs(absorption):
    deviation = 1
    C = referenceCurve()
    curve = list(C.values())
    subsetAbs = {k: absorption[k] for k in C.keys()}
    subset_list = list(subsetAbs.values())
    while deviation > 0.10:
        diff = [a - b for a, b in zip(curve, subset_list)]
        diff = [0 if x < 0 else x for x in diff ]
        deviation = sum(diff)
        if deviation > 0.10:
            curve = [x-0.05 for x in curve]
        else:
            break
    alpha = round(curve[1],2)
    return alpha

def shapeIndicator(absorption, alpha):
    C = referenceCurve()
    diff = 1.00 - alpha
    curve = {k: C[k]-diff for k in C.keys()}
    frequencyIndicator = ''
    if absorption[250]-curve[250] > 0.25:
        frequencyIndicator = frequencyIndicator + 'L'
    if absorption[500]-curve[500] > 0.25 or absorption[1000]-curve[1000] > 0.25:
        frequencyIndicator = frequencyIndicator + 'M'
    if absorption[2000]-curve[2000] > 0.25 or absorption[4000]-curve[4000] > 0.25:
        frequencyIndicator = frequencyIndicator + 'H'
    if frequencyIndicator == '':
        frequencyIndicator = 'N/A'
    return frequencyIndicator

def soundAbsorptionClass(alpha):
    if alpha >= 0.90:
        saClass = 'A'
    elif alpha >= 0.80 and alpha < 0.90:
        saClass = 'B'
    elif alpha >= 0.60 and alpha < 0.80:
        saClass = 'C'
    elif alpha >= 0.30 and alpha < 0.6:
        saClass = 'D'
    elif alpha >= 0.15 and alpha < 0.25:
        saClass = 'E'
    else:
        saClass = 'Not Classified'
    return saClass

def NRC(absorption):
    total = absorption[250] + absorption[500] + absorption[1000] + absorption[2000]
    return round(total/(4*0.05), 0)*0.05

def SAA(absorption):
    total = (absorption[500] + absorption[630] + absorption[800] + absorption[1000] +
             absorption[1250] + absorption[1600] + absorption[2000] + absorption[2500] +
             absorption[3150] + absorption[4000] + absorption[5000])
    saa = total/8
    return saa