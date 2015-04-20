import numpy as np


def get_focii(spacing_of_elements):
    c = spacing_of_elements / 2
    return c


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
