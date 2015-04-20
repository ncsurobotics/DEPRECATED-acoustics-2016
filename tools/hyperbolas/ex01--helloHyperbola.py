import matplotlib.pyplot as plt

from .common import get_focii, hyperbola, hyperbolaCOE

# Initialize parameters
d = 12.01e-2  # Hydrophone spacing (meters)
del_t = 67.889e-6 / 10  # time difference in signal arrival (seconds)
v = 1473  # Speed of sound in the medium (m/s)

# Settings
sz = "small"


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
