import pandas as pd
import numpy as np

import calculateReverberationTimes

#####################
# data = np.load(r"D:\ReverberationRoom\filter-testing\20200202_test13\20200202_test13.npy")
# data = np.load(r"L:\Project files 2020\New folder\15mm NDF 15mm CMAX20mm run3.npy")

# rt = calculateReverberationTimes.performRTcalculation(data=data, volume=219, temp=20.5, relativeHumidity=63, pressure=101, db_decay='t30', decay_time=5)

# rt.to_csv(r'D:\RT20200203\CmaxTests\20200203_15mmNDF15mmCMAX20mm_run3_t30.csv')

# ###################
# data = np.load(r"L:\Project files 2020\New folder\15mm NDF 15mm CMAX20mm run2.npy")

# rt = calculateReverberationTimes.performRTcalculation(data=data, volume=219, temp=20.5, relativeHumidity=63, pressure=101, db_decay='t30', decay_time=5)

# rt.to_csv(r'D:\RT20200203\CmaxTests\20200203_15mmNDF15mmCMAX20mm_run2_t30.csv')

# ##################
# data = np.load(r"L:\Project files 2020\New folder\15mm NDF 15mm CMAX20mm run1.npy")

# rt = calculateReverberationTimes.performRTcalculation(data=data, volume=219, temp=20.5, relativeHumidity=63, pressure=101, db_decay='t30', decay_time=5)

# rt.to_csv(r'D:\RT20200203\CmaxTests\20200203_15mmNDF15mmCMAX20mm_run1_t30.csv')

##################
data = np.load(r"L:\Project files 2020\New folder\empty room.npy")

rt = calculateReverberationTimes.performRTcalculation(data=data, volume=219, temp=20.5, relativeHumidity=63, pressure=101, db_decay='t30', decay_time=5)

rt.to_csv(r'D:\RT20200203\CmaxTests\20200203_empty_t30.csv')