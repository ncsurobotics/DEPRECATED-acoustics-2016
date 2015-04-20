import numpy as np
import matplotlib.pyplot as plt


def Isolate(y):
    # Initialize parameters
    buf = 0
    thr = 0.02

    # Initialize parameters for start point
    v = 0
    m = -1

    # Compute start point
    while v < thr:
        m += 1
        v = y[m]
    start = m - buf

    # Initialize parameters for end point
    v = 0
    m = y.size

    # Compute endpoint
    while v < thr:
        m -= 1
        v = y[m]
    end = m + buf

    return (start, end)


def FFT(x, fs):
    # Initialize parameters
    M = x.size
    Theta_s = 2 * np.pi / M
    X = [0] * M
    for k in range(M):
        DFT = 0
        for m in range(M):
            a = x[m] * np.exp(1j * m * Theta_s * k)
            DFT += a

        X[k] = DFT / M

    return X


class BBB:

    def __init__(self):
        pass

    def Vectorize1(self, y, fs, target_freq):
        n = y.shape[0]  # n elements/channels
        y_slice = [0] * n
        Y = [0] * n

        # Let's see if we can get the ball rolling by obtaining the phase of just one channel
        # Slice channels to particular length based on pulse length
        (start, end) = Isolate(y[0])
        y_slice[0] = y[0][start:end]
        M = y_slice[0].size

        # Generate dft related parameters
        f_delta = fs / M
        fbin_target = int(round(target_freq / f_delta))
        f_start = (fbin_target - 0.5) * f_delta
        f_stop = (fbin_target + 0.5) * f_delta
        print("bin size is %dHz. That means that the you can inspect the component from %gHz to %gHz."
              % (f_delta, f_start, f_stop))

        # Compute Freq spectrum
        Y[0] = FFT(y_slice[0], fs)

        # Plot Freq spectrum
        f, ax = plt.subplots(1, sharex=True)
        ax.plot(np.arange(M) * f_delta, np.absolute(Y[0]))
        ax.set_title('Freq Spec for sliced pulse')

        # measure phase
        theta = np.angle(Y[0][fbin_target], deg=True)

        print("Phase = %d degrees." % theta)

        # Determine phase of 22khz signal
