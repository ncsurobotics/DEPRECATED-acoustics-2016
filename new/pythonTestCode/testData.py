from fft import calcOrientation
import numpy as np
import matplotlib.pyplot as plt


data = np.genfromtxt("../T1M.csv", delimiter=",", skip_header=2)
print("Data received")
pf = 22e3
Fs = 250e6
num_periods = 8
output = []



inputSize = int(Fs/pf  * num_periods)
for i in range(0, int(data.size / 5 - inputSize), inputSize):
    print("Starting calculation")
    yaw, pitch = calcOrientation(data[i:i+inputSize, :], Fs, pf, True)
    print(str(i) + ":" + str(yaw) + "," + str(pitch))
    output.append([i, yaw, pitch])
    

print(output)
np.savetxt("data/processed/conf1.csv", output, delimiter=",", header="T, yaw, pitch")

