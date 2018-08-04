from fft import calcOrientation
import numpy as np
import matplotlib.pyplot as plt


data = np.genfromtxt("./data/ping45far1new5Mhz.csv", delimiter=",", skip_header=0)
print("Data received")
pf = 22e3
Fs = 5e6
yaw, pitch,good = calcOrientation(data.transpose()[200:1000, :], Fs, pf, True)
print("YAW: " + str(yaw) + ","  "PITCH:" + str(pitch))


