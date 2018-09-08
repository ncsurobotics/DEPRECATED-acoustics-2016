from fft import calcOrientation
import sys
import numpy as np
import matplotlib.pyplot as plt
from simulator import *


c = 1484
hydrophones = np.array([[0,       -0.1,   0],
                        [0,       -0.119, 0],
                        [0.0095,   0,     0],
                        [-0.0095,  0,     0]])
data = np.genfromtxt("../Waveforms/conf" + sys.argv[1] + "/Settings4/Test" + sys.argv[2] + ".csv", delimiter=",", skip_header=3)
#data = data[int(sys.argv[1]):int(sys.argv[2])]
data = data[1100:1800]
t = data[:, 0]
ch1 = data[:,1]
ch2 = data[:,2]
ch3 = data[:,3]
ch4 = data[:,4]

ch2_shift = np.argmax(np.correlate(ch1, ch2, "same")) - int(len(data) / 2)
ch3_shift = np.argmax(np.correlate(ch1, ch3, "same")) - int(len(data) / 2)
ch4_shift = np.argmax(np.correlate(ch1, ch4, "same")) - int(len(data) / 2)
dt = t[1] - t[0]


plt.figure()
plt.plot(t, ch1)
plt.plot(t, np.roll(ch2, ch2_shift))
plt.plot(t, np.roll(ch3, ch3_shift))
plt.plot(t, np.roll(ch4, ch4_shift))
plt.show()

print(ch2_shift * c * dt / 1000, ch3_shift * c * dt / 1000, ch4_shift * c * dt / 1000)


