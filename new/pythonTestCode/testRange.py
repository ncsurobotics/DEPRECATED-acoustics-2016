from fft import calcOrientation
import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt("../Waveforms/conf1/Settings4/Test1.csv", delimiter=",", skip_header=3)
print("Data received")
pf = 22e3
Fs = 2.4046e6
num_periods = 8
output = []

start = 1400
end = 1600
plt.plot(data[start:end, 1:5])
plt.show()
print("Starting calculations")
yaw, pitch = calcOrientation(data[start:end, 1:5], Fs, pf, True)
print(str(yaw) + "," + str(pitch))
input("Press Enter to continue ...")
exit()
