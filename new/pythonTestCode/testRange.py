from fft import calcOrientation
import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt("simulated.csv", delimiter=",", skip_header=2)
print("Data received")
pf = 22e3
Fs = 1000e3
num_periods = 8
output = []

start = 200
end = 500
#plt.plot(data[:, 0:4])
#plt.show()
print("Starting calculations")
yaw, pitch = calcOrientation(data[start:end, :], Fs, pf, True)
print(str(yaw) + "," + str(pitch))
input("Press Enter to continue ...")
exit()

    


