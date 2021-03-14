import helpers
import numpy as np

Fs = 50000
T = 600


pink1 = helpers.generatePinkNoise(t=T, fs=Fs)
white1 = helpers.generateWhiteNoise(t=T, fs=Fs)

np.save('pinkNoise1', pink1)
np.save('whiteNoise1', white1)

pink2 = helpers.generatePinkNoise(t=T, fs=Fs)
white2 = helpers.generateWhiteNoise(t=T, fs=Fs)

np.save('pinkNoise2', pink2)
np.save('whiteNoise2', white2)