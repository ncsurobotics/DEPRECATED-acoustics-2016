import matplotlib.pyplot as plt
import numpy as np
import itertools

from .common import get_focii, hyperbola, hyperbolaCOE, xform_rotate, xform_translate


def easyHyperbola(d, del_t, v):
    # Compute first hyperbola
    c = get_focii(d)
    (a, b) = hyperbolaCOE(c, del_t, v)
    (x, y) = hyperbola(a, b)
    hbla = np.vstack((x, y))
    return hbla


def go(src_loc, n, bs):
    # Initialize parameters
    x = 0
    y = 1

    # Initialize plot
    fig1, ax1 = plt.subplots()
    ax1.set_title("Hydrophone Array")
    zoom = 200e-2
    ax1.axis(xmin=-zoom,
             xmax=zoom,
             ymin=-zoom,
             ymax=zoom)

    v = 1473  # Speed of sound in the medium (m/s)

    # Plot something we already know
    plt.plot(src_loc[x], src_loc[y], 'x')
    for i in range(n):
        plt.plot(bs[i][x], bs[i][y], 'ro')

    for ID in itertools.combinations(range(3), 2):
        # Set parameters and establish system for accessing elements
        print("go: Working on combo %s and %s" % (ID[0], ID[1]))
        el = [0, 0]
        el[0] = bs[ID[0]]
        el[1] = bs[ID[1]]

        # Determine COMes and Rotations necessary to access individual elements
        COM_i = (el[0] + el[1]) / 2
        tangent_i = el[1] - el[0]
        rot_i = np.arctan2(tangent_i[y], tangent_i[x])[0]

        print("The rotation of this pair is %.1f radians." % rot_i)

        # Calculate del_t
        D1 = np.linalg.norm(el[0] - src_loc)
        D2 = np.linalg.norm(el[1] - src_loc)
        del_t = (D1 - D2) / v

        # Generate boolean for left or right
        if del_t > 0:
            r_bit = 1
        elif del_t < 0:
            r_bit = -1
            del_t = del_t * -1

        # Calculate the hyperbola
        d = np.linalg.norm(el[1] - el[0])
        hbla_o = easyHyperbola(d, del_t, v)

        # select "side of hyperbola based on sign"
        hbla_o = hbla_o * np.array([[r_bit], [1]])

        # rotate hyperbola to the appropriate location
        hbla_o = xform_rotate(hbla_o, rot_i)
        hbla_i = xform_translate(hbla_o, COM_i[x][0], COM_i[y][0])

        # PLOT!!!
        plt.plot(hbla_i[x], hbla_i[y])

        # DEBUG plt.plot(center[x], center[y], 'x')
        print("")

    # Commit the final plot
    plt.show()


def main():
    Hyd = [np.array([[0], [10e-2]])]  # Hydrophone #1 location (meters)
    Hyd.append(xform_rotate(Hyd[0], 2 * np.pi / 3))
    Hyd.append(xform_rotate(Hyd[1], 2 * np.pi / 3))

    src = np.array([[2e-2], [2e-2]])

    go(src, 3, Hyd)

print("-" * 50)
main()
