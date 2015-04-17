import matplotlib.pyplot as plt
import numpy as np

from .common import get_focii

# Initialize parameters
d = 12.01e-2  # Hydrophone spacing (meters)
del_t = 67.889e-6 / 10  # time difference in signal arrival (seconds)
v = 1473  # Speed of sound in the medium (m/s)

# Settings
sz = "small"


def hyperbola(a, b):
    step = .1e-2
    y = np.arange(-200, 200 + step, step)
    x = a * np.sqrt(1 + (y / b)**2)
    return (x, y)


def hyperbolaCOE(c, del_t, v_medium):
    # Compute a
    del_d = del_t * v
    a = del_d / 2

    # check for error
    if a > c:
        print("hyperbolaCOE: ERROR. Your a, --%.1fcm--, is greater than c, --%.1fcm--. Please reduce time delay or increase element spacing."
              % (a * 100, c * 100))
        exit(1)

    # Compute b
    b = np.sqrt(c**2 - a**2)

    # Explain and return
    print("""hyperbolaCOE: I see you have a measured time delay of %.1f microseconds and the speed of sound in your medium is %d m/s. Given that your elements are %.1f cm appart, then a = %.1fcm, and b = %.1fcm."""
          % (del_t * 1e6, v_medium, 2 * c * 100, a * 100, b * 100))
    return (a, b)


def main():
    # Compute first hyperbola
    c = get_focii(d)
    (a, b) = hyperbolaCOE(c, del_t, v)
    (x, y) = hyperbola(a, b)

    # Plot yo work!
    fig1, ax1 = plt.subplots()
    ax1.set_xlabel("x (meters)")
    ax1.set_ylabel("y (meters)")
    if sz == "large":
        ax1.set_title("(Zoomed out) X-Y plane of possible signal src. locations")
        ax1.axis(xmin=-51,
                 xmax=51,
                 ymin=-2,
                 ymax=100)
    elif sz == "small":
        ax1.set_title("X-Y plane of possible signal src. locations")
        ax1.axis(xmin=-10e-2,
                 xmax=10e-2,
                 ymin=-10e-2,
                 ymax=10e-2)

    ax1.plot(d / 2, 0, 'ro')  # Plot focii
    ax1.plot(-d / 2, 0, 'ro')
    ax1.plot(x, y)  # hyperbola
    ax1.plot(-x, y)
    plt.show()

print("-" * 50)
main()
