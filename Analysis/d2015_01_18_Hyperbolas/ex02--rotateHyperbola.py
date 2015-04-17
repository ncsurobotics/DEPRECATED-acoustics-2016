import matplotlib.pyplot as plt
import numpy as np

from .common import get_focii


def hyperbola(a, b):
    step = .1e-2
    y = np.arange(-200, 200 + step, step)
    x = a * np.sqrt(1 + (y / b)**2)
    return (x, y)


def hyperbolaCOE(c, del_t, v_medium):
    # Compute a
    del_d = del_t * v_medium
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


def easyHyperbola(d, del_t, v):
    # Compute first hyperbola
    c = get_focii(d)
    (a, b) = hyperbolaCOE(c, del_t, v)
    (x, y) = hyperbola(a, b)
    return (x, y)


def xform_rotate(xy, theta):
    a11 = np.cos(theta)
    a12 = -np.sin(theta)
    a21 = np.sin(theta)
    a22 = np.cos(theta)
    A = np.array([[a11, a12], [a21, a22]])

    # transform
    xy = np.dot(A, xy)

    return xy


def xform_translate(xy, x_shift, y_shift):
    xy = xy + np.array([[x_shift], [y_shift]])
    return xy


def main():
    # Initialize parameters
    d = 12.01e-2  # Hydrophone spacing (meters)
    del_t = 67.889e-6  # time difference in signal arrival (seconds)
    v = 1473  # Speed of sound in the medium (m/s)

    # empty stuff
    x = 0
    y = 1

    # Settings
    sz = "small"

    # Create Primitive environment
    (hbla_x, hbla_y) = easyHyperbola(d, del_t, v)
    hbla2 = np.vstack((hbla_x, hbla_y))
    hbla1 = hbla2 * np.array([[-1], [1]])
    hyd1 = np.array([[-d / 2], [0]])
    hyd2 = np.array([[d / 2], [0]])

    # Perform Transformations
    rot_val = np.pi / 3
    hbla1 = xform_rotate(hbla1, rot_val)
    hbla2 = xform_rotate(hbla2, rot_val)
    hyd1 = xform_rotate(hyd1, rot_val)
    hyd2 = xform_rotate(hyd2, rot_val)

    x_sh = 10e-2
    y_sh = 5e-2
    hbla1 = xform_translate(hbla1, x_sh, y_sh)
    hbla2 = xform_translate(hbla2, x_sh, y_sh)
    hyd1 = xform_translate(hyd1, x_sh, y_sh)
    hyd2 = xform_translate(hyd2, x_sh, y_sh)

    # Plot yo work!
    fig1, ax1 = plt.subplots()
    ax1.set_xlabel("x (meters)")
    ax1.set_ylabel("y (meters)")
    ax1.grid(b=True)
    if sz == "large":
        ax1.set_title("(Zoomed out) X-Y plane of possible signal src. locations")
        ax1.axis(xmin=-51,
                 xmax=51,
                 ymin=-2,
                 ymax=100)
    elif sz == "small":
        ax1.set_title("X-Y plane of possible signal src. locations")
        zoom = 20e-2
        ax1.axis(xmin=-zoom,
                 xmax=zoom,
                 ymin=-zoom,
                 ymax=zoom)

    ax1.plot(hyd1[x], hyd1[y], 'ro')  # Plot focii
    ax1.plot(hyd2[x], hyd2[y], 'ro')
    ax1.plot(hbla1[x], hbla1[y])  # hyperbola
    ax1.plot(hbla2[x], hbla2[y])  # hyperbola
    # ax1.plot(-x,y)
    plt.show()

print("-" * 50)
main()
