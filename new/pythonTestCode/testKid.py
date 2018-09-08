import sys
import numpy as np
import matplotlib.pyplot as plt



hydrophones = np.array([[0,       -0.1,   0],
                        [0,       -0.119, 0],
                        [0.0095,   0,     0],
                        [-0.0095,  0,     0]])

def calcOrientation(tdoa):


    SPEED_OF_SOUND = 1484
    sideToSideDistance = np.linalg.norm(hydrophones[3] - hydrophones[2]) / 2
    inlineDistance = np.linalg.norm(hydrophones[1] - hydrophones[0]) / 2 

    sideToSideA = tdoa[1] * SPEED_OF_SOUND / 2
    sideToSideB = np.sqrt(sideToSideDistance ** 2 - sideToSideA ** 2)

    inlineA = tdoa[0] * SPEED_OF_SOUND / 2
    inlineB = np.sqrt(inlineDistance ** 2 - inlineA ** 2)

    front = np.sign(inlineA)

    yaw = np.arctan2(-sideToSideA, front * sideToSideB)
    pitch = np.arctan2(inlineA, inlineB)

    return (np.rad2deg(yaw), np.rad2deg(pitch))
    

data = np.genfromtxt("../competition/45degKidPool/ping3.csv", delimiter=",", skip_header=3)
#data = data[int(sys.argv[1]):int(sys.argv[2])]
data = data[:]
t = data[:, 0]
ch1 = data[:,1]
ch2 = data[:,2]
ch3 = data[:,3]
ch4 = data[:,4]

plt.figure()
plt.title("Raw data channels 1 and 2")
plt.plot(t, ch1)
plt.plot(t, ch2)
plt.show(block=False)



ch2_shift = np.argmax(np.correlate(ch1, ch2, "same")) - int(len(data) / 2)

ch4_shift = np.argmax(np.correlate(ch3, ch4, "same")) - int(len(data) / 2)
dt = t[1] - t[0]
yaw, pitch = calcOrientation([-ch4_shift * dt / 1000, - ch2_shift * dt / 1000])
print(yaw, pitch)

plt.figure()
plt.title("Shifted data channels 1 and 2")
plt.plot(t, ch1)
plt.plot(t, np.roll(ch2, ch2_shift))
plt.show(block=False)


plt.figure()
plt.plot(t, ch3)
plt.plot(t, ch4)
plt.show(block=False)

plt.figure()
plt.title("Shifted data channels 3 and 4")
plt.plot(t, ch3)
plt.plot(t, np.roll(ch4, ch4_shift))

plt.show()


