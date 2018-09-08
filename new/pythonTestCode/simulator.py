import numpy as np
import matplotlib.pyplot as plt
import sys
v_sound = 1530
f_s = 10e6
f_pinger = 42e3


left = np.array([-0.0095, 0, 0])
right =  np.array([0.0095,0, 0.])
front = np.array([0, -0.1, 0])
back = np.array([0, -0.119, 0.0])

hydrophones = [left, right, front, back]

pinger_locs = np.array([[1.09, 1.03, 1.16],
                        [1.09, 0.54, 1.16],
                        [0.65, 1.16, 0.55],
                        [0.00, 0.98, 2.25],
                        [10.0, -12.0, 10.0]])

pinger_loc = pinger_locs[0]
tdoas = []

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return (idx, array[idx])


def calcTDOA(left=left, right=right, pinger=pinger_loc):
    distance_left = np.linalg.norm(left - pinger)
    distance_right = np.linalg.norm(right - pinger)

    t_left = distance_left / v_sound
    t_right = distance_right / v_sound

    return t_left - t_right

def calcTOA(hydrophone, pinger):
    distance = np.linalg.norm(hydrophone - pinger)
    return distance / v_sound

def rot(left=left, right=right, pinger_loc=pinger_loc):
    tdoas = []
    for yaw in np.arange(-180, 180):
        radians = np.deg2rad(yaw)
        rotation_matrix = [[np.cos(radians), -np.sin(radians), 0], [np.sin(radians), np.cos(radians), 0], [0, 0, 1]]
        cur_left = np.matmul(left, rotation_matrix)
        cur_right = np.matmul(right, rotation_matrix)
        tdoa = calcTDOA(cur_left, cur_right, pinger_loc)
        tdoas.append(tdoa * 1000)
     
    return np.array(tdoas)

def mlat(pinger_loc=pinger_loc):
    t_0 = calcTOA(hydrophones[0], pinger_loc)
    vt_0 = v_sound * t_0
    x_0 = hydrophones[0][0]
    y_0 = hydrophones[0][1]
    z_0 = hydrophones[0][2]

    lhs = np.zeros(shape=(3, 3))
    rhs = np.zeros(shape=(3))


    for i in range(1, 4):
        t_m = calcTOA(hydrophones[i], pinger_loc)
        vt_m = v_sound * t_m

        x_m = hydrophones[i][0]
        y_m = hydrophones[i][1]
        z_m = hydrophones[i][2]

        a = 2 * x_m / vt_m - 2 * x_0 / vt_0
        b = 2 * y_m / vt_m - 2 * y_0 / vt_0
        c = 2 * z_m / vt_m - 2 * z_0 / vt_0
        d = vt_m - vt_0 \
            - (x_m ** 2 + y_m ** 2 + z_m ** 2) / vt_m \
            + (x_0 ** 2 + y_0 ** 2 + z_0 ** 2) / vt_0

        lhs[i - 1] = [a, b, c]
        rhs[i - 1] = -d
    #print(lhs, rhs)
    return np.linalg.solve(lhs, rhs) * 2

