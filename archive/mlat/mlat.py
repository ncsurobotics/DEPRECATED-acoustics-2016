#!/usr/bin/env python

import time
import random


def eq(a, b, err=1e-5):
    return (abs(a - b) < err)


def mlat(receivers, delays, V=1497.0):
    x = [0, 0, 0, 0]
    y = [0, 0, 0, 0]
    z = [0, 0, 0, 0]

    x_i, y_i, z_i = map(float, receivers[0])
    x_j, y_j, z_j = map(float, receivers[1])
    x_k, y_k, z_k = map(float, receivers[2])
    x_l, y_l, z_l = map(float, receivers[3])

    R_ij = V * float(delays["ij"])
    R_ik = V * float(delays["ik"])
    R_kj = V * float(delays["kj"])
    R_kl = V * float(delays["kl"])

    x_ji = x_j - x_i
    x_jk = x_j - x_k
    x_lk = x_l - x_k
    x_ki = x_k - x_i

    y_ji = y_j - y_i
    y_jk = y_j - y_k
    y_lk = y_l - y_k
    y_ki = y_k - y_i

    z_ji = z_j - z_i
    z_jk = z_j - z_k
    z_lk = z_l - z_k
    z_ki = z_k - z_i

    A = (R_ik * x_ji - R_ij * x_ki) / (R_ij * y_ki - R_ik * y_ji)
    B = (R_ik * z_ji - R_ij * z_ki) / (R_ij * y_ki - R_ik * y_ji)
    C = ((R_ik * (R_ij**2 + x_i**2 - x_j**2 + y_i**2 - y_j**2 + z_i**2 - z_j**2)) -
         (R_ij * (R_ik**2 + x_i**2 - x_k**2 + y_i**2 - y_k**2 + z_i**2 - z_k**2))) / (2 * (R_ij * y_ki - R_ik * y_ji))
    D = (R_kl * x_jk - R_kj * x_lk) / (R_kj * y_lk - R_kl * y_jk)
    E = (R_kl * z_jk - R_kj * z_lk) / (R_kj * y_lk - R_kl * y_jk)
    F = ((R_kl * (R_kj**2 + x_k**2 - x_j**2 + y_k**2 - y_j**2 + z_k**2 - z_j**2)) -
         (R_kj * (R_kl**2 + x_k**2 - x_l**2 + y_k**2 - y_l**2 + z_k**2 - z_l**2))) / (2 * (R_kj * y_lk - R_kl * y_jk))

    # Set to 1 if both numerator and denominator are near 0
    if eq(E - B, 0) and eq(A - D, 0):
        G = 1.0
    else:
        G = (E - B) / (A - D)

    # Set to 1 if both numerator and denominator are near 0
    if eq(F - C, 0) and eq(A - D, 0):
        H = 1.0
    else:
        H = (F - C) / (A - D)

    I = A * G + B
    J = A * H + C
    K = R_ik**2 + x_i**2 - x_k**2 + y_i**2 - y_k**2 + z_i**2 - z_k**2 + 2 * x_ki * H + 2 * y_ki * J
    L = 2 * (x_ki * G + y_ki * I + 2 * z_ki)
    M = (4 * R_ik**2 * (G**2 + I**2 + 1)) - L**2
    N = (8 * R_ik**2 * (G * (x_i - H) + I * (y_i - J) + z_i)) + 2 * L * K
    O = (4 * R_ik**2 * ((x_i - H)**2 + (y_i - J)**2 + z_i**2)) - K**2

    z_0 = (N / (2 * M)) + ((N / (2 * M))**2 - (O / M))**0.5
    x_0 = G * z_0 + H
    y_0 = I * z_0 + J
    sol_0 = (x_0, y_0, z_0)
    err_0 = solution_error(receivers, delays, sol_0, V)

    z_1 = (N / (2 * M)) - ((N / (2 * M))**2 - (O / M))**0.5
    x_1 = G * z_1 + H
    y_1 = I * z_1 + J
    sol_1 = (x_1, y_1, z_1)
    err_1 = solution_error(receivers, delays, sol_1, V)

    if err_0 < err_1:
        return sol_0, sol_1
    else:
        return sol_1, sol_0


def solution_error(receivers, delays, solution, V=1497.0):
    t = 4 * [0]
    comp_delays = dict()

    x, y, z = solution
    x_i, y_i, z_i = receivers[0]
    x_j, y_j, z_j = receivers[1]
    x_k, y_k, z_k = receivers[2]
    x_l, y_l, z_l = receivers[3]

    t_i = (((x - x_i)**2 + (y - y_i)**2 + (z - z_i)**2) ** 0.5) / V
    t_j = (((x - x_j)**2 + (y - y_j)**2 + (z - z_j)**2) ** 0.5) / V
    t_k = (((x - x_k)**2 + (y - y_k)**2 + (z - z_k)**2) ** 0.5) / V
    t_l = (((x - x_l)**2 + (y - y_l)**2 + (z - z_l)**2) ** 0.5) / V

    comp_delays["ij"] = (t_i - t_j)
    comp_delays["ik"] = (t_i - t_k)
    comp_delays["kj"] = (t_k - t_j)
    comp_delays["kl"] = (t_k - t_l)
    err = sum([(comp_delays[p] - delays[p])**2 for p in ["ij", "ik", "kj", "kl"]])

    return err


def test_0():
    receivers = [(0., 0., 0.),
                 (1., 0., 0.),
                 (0., 1., 0.),
                 (1., 1., 0.)]

    t = [0, 0, 0, 0]
    t[0] = 3 / 1497.
    t[1] = 6**0.5 / 1497.
    t[2] = 6**0.5 / 1497.
    t[3] = 3**0.5 / 1497.

    delay = dict()
    delay["ij"] = (t[0] - t[1])
    delay["ik"] = (t[0] - t[2])
    delay["kj"] = (t[2] - t[1])
    delay["kl"] = (t[2] - t[3])

    t_0 = time.time()
    x, y, z = mlat(receivers, delay)[0]
    t_1 = time.time()

    print "Solution should be approximately (2, 2, 1)"
    print " (%.3f, %.3f, %.3f)" % (x, y, z)
    print "Time to find solution: %0.6f" % (t_1 - t_0,)


def test_1():
    receivers = [(0, 26566800, 0),
                 (-15338349, 15338349, 15338349),
                 (0, 6380000, 25789348),
                 (-18785564, 18785564, 0)]

    t = [0, 0, 0, 0]
    t[0] = 67335898e-9
    t[1] = 78283279e-9
    t[2] = 86023981e-9
    t[3] = 75092320e-9

    delay = dict()
    delay["ij"] = (t[0] - t[1])
    delay["ik"] = (t[0] - t[2])
    delay["kj"] = (t[2] - t[1])
    delay["kl"] = (t[2] - t[3])

    t_0 = time.time()
    x, y, z = mlat(receivers, delay, 2.99792458e8)[0]
    t_1 = time.time()

    print "Solution should be approximately (0, 638000, 0)"
    print " (%d, %d, %d)" % (int(round(x / 100) * 100),
                             int(round(y / 100) * 100),
                             int(round(z / 100) * 100))
    print "Time to find solution: %0.6f" % (t_1 - t_0,)


def dist(a, b):
    return ((a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2)**0.5


def gen_tests(n=100, V=1497.0):
    receivers = [(0., 0., 0.),
                 (1., 2., 0.),
                 (-1., 2., 0.),
                 (0., 1., 1.)]

    corr_noise_mag = 20e-6
    scale = 100

    x_i, y_i, z_i = map(float, receivers[0])
    x_j, y_j, z_j = map(float, receivers[1])
    x_k, y_k, z_k = map(float, receivers[2])
    x_l, y_l, z_l = map(float, receivers[3])

    random.seed()
    good = 0

    for i in range(0, n):
        x, y, z = [(2 * random.random() - 1) * 10 for j in range(0, 3)]

        # Compute actual time delays
        t_i = ((x - x_i)**2 + (y - y_i)**2 + (z - z_i)**2) ** 0.5 / V
        t_j = ((x - x_j)**2 + (y - y_j)**2 + (z - z_j)**2) ** 0.5 / V
        t_k = ((x - x_k)**2 + (y - y_k)**2 + (z - z_k)**2) ** 0.5 / V
        t_l = ((x - x_l)**2 + (y - y_l)**2 + (z - z_l)**2) ** 0.5 / V

        delay = dict()
        delay["ij"] = (t_i - t_j)
        delay["ik"] = (t_i - t_k)
        delay["kj"] = (t_k - t_j)
        delay["kl"] = (t_k - t_l)

        if corr_noise_mag:
            delay["ij"] += (corr_noise_mag * random.normalvariate(0, 0.2))
            delay["ik"] += (corr_noise_mag * random.normalvariate(0, 0.2))
            delay["kj"] += (corr_noise_mag * random.normalvariate(0, 0.2))
            delay["kl"] += (corr_noise_mag * random.normalvariate(0, 0.2))

        try:
            solutions = mlat(receivers, delay, V)
        except:
            print "(%d) COULD NOT COMPUTE" % (i,)
            continue
        err = 1

        if dist(solutions[0], (x, y, z)) > err and dist(solutions[1], (x, y, z)) > err:
            print "(%d) WARNING:" % (i,)
            print "Expected: (%5.2f, %5.2f, %5.2f)" % (x, y, z)
            print "Computed: (%5.2f, %5.2f, %5.2f)" % solutions[0]
            print "          (%5.2f, %5.2f, %5.2f)" % solutions[1]
            print
        else:
            good += 1
    print "Done (%.2f)" % (float(good) / n)

if __name__ == "__main__":
    gen_tests(1000)
    # test_0()
    # test_1()
