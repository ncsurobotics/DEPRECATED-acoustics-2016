#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=too-many-ancestors
# pylint: disable=invalid-variable-name

"""
ZetCode Tkinter tutorial

This program creates a Quit
button. When we press the button,
the application terminates.

Author: Jan Bodnar
Last modified: November 2015
Website: www.zetcode.com
"""
import time
import threading

from Tkinter import Tk, BOTH, TOP, RIGHT, LEFT
from ttk import Frame, Button, Style

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.animation as animation

from numpy import arange, sin, pi
import numpy as np

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 200

HZ60 = 16


class SubFrame(Frame):
    """The main object for placing stuff in the GUI. It's treated as a
    section object, whereby we can divide up the window into sections."""

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

    def add_button(self, name, func, loc):
        """Adds a button in the desired location of the SubFrame"""

        # set title of button
        button = Button(self, text=name, command=func)

        # place the button
        button.place(x=loc[0], y=loc[1])
        self.pack(side=LEFT, fill=BOTH, expand=1)


class TkManager():

    def __init__(self):
        self.root = Tk()
        self.style = None

        # object placeholder
        self.mpl_canvas = None
        self.button_frame = None

    def init(self):
        # create a window
        self.place_window(WINDOW_WIDTH, WINDOW_HEIGHT)

        # set name of the window
        self.root.title = ("Quit")

        # stylize everything
        self.style = Style()
        self.style.theme_use('clam')

    def auto_populate(self):
        """automatically does the layout stuff for this program"""
        # create a button frame object
        self.button_frame = SubFrame(self.root)
        button_frame = self.button_frame

        # Add buttons to the GUI
        button_frame.add_button('quit', button_frame.quit, [5, 5])


        if self.mpl_canvas is not None:
            # attach matplotlib gui
            mpl_widget = self.mpl_canvas.get_tk_widget()
            mpl_widget.pack(side=RIGHT, fill=BOTH, expand=1)
        else:
            print "Missing matplotlib canvas"


    def place_window(self, x_dim, y_dim):
        """Places the window in the top left corner of screen.
        User may specify dimensions."""
        x = str(x_dim)
        y = str(y_dim)
        dim = x + 'x' + y
        self.root.geometry(dim + '+20+50')

    def run(self):
        self.root.mainloop()

    def getRoot(self):
        return self.root

    def attach_mpl(self, mpl_figure):
        self.mpl_canvas = FigureCanvasTkAgg(mpl_figure, master=self.root)

    def attach_thread(self, func, waittime):
        self.root.after(waittime, func, (self.root, waittime))


class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.initUI()

    def initUI(self):

        self.parent.title("Quit button")
        self.style = Style()
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)

        quitButton = Button(self, text="Quit",
                            command=self.quit)
        quitButton.place(x=50, y=50)


class Acoustics():
    """class for communicating with acoustics board and updating
    relevent acoustics information"""

    def __init__(self):
        # state flag
        self.state = ['init', None, None, None]
        self.mpl_fig = None
        self.port = None
        self.axes = None
        self.lines = [None, None, None, None]

        self.rx_thread = threading.Thread(name="rx", target=self.rx_loop)
        self.exit_flg = threading.Event()
        self.data_lock = threading.Lock()
        self.network_disconnect_flg = threading.Event()

        # fake data parameters
        self.fake_data_rate = 1000.0 #hz

        # data attribute
        self.counter = 0

        # acoustics handles
        self.data_channels = ['CHA0','CHA1','CHB0','CHB1']

    def rx_loop(self):
        """Main thread for communicating with the acoustics module.
        """

        # enter while loop
        while self.exit_flg.isSet() is False:

            network = False
            if network is False:
                if self.network_disconnect_flg.isSet() is False:
                    print "[Acoustics RX Thread]: Network is not active"
                    self.network_disconnect_flg.set()

                with self.data_lock:
                    self.counter += 1
                time.sleep(1.0/self.fake_data_rate)

            else:
                msg = self.port.recv()
                print msg

    def attach_mpl_figure(self, f):
        self.mpl_fig = f
        self.axes = f.add_subplot(111)

    def start(self):
        self.rx_thread.start()

    def check_net(self):
        pass

    def update_plot(self, t, y_vectors):
        """method to facilitate plotting data on the
        main graph. 
        args:
          t -- list of time values for the x axis. A list
          of length 0 is interpreted as an instruction to 
          not update the x axis.

          y_vectors -- a list of 1D vectors corresponding
          to the y values of each trace."""

        n_traces = len(y_vectors)

        if t is not None:
            # update the x axis
            for i in range(n_traces):
                self.lines[i].set_xdata(t)

        for i in range(n_traces):
            # update each y axis
            y = y_vectors[i]
            self.lines[i].set_ydata(y)

    def fake_get_data(self):
        t = arange(0.0, 3.0, 0.01)

        with self.data_lock:
            s1 = sin(2 * pi * t + self.counter/100.0) * sin(2 * pi * t/2.0 + self.counter/2000.0)
            s3 = sin(2 * pi * t*1.5 + self.counter/100.0) * sin(2 * pi * t/2.0 + self.counter/800.0)
            s2 = sin(0*t)
            s4 = sin(0*t)
        y = [s1,s2,s3,s4]
        return y


    def init_graph(self):
        """Puts an empty graph in the GUI."""
        t = arange(0.0, 3.0, 0.01)
        s = sin(0 * t)

        for i in range(len(self.lines)):
            name = self.data_channels[i]
            self.lines[i], = self.axes.plot(t, s, label=name)

        # Setup layout
        self.axes.set_ylim([-5,5])
        self.axes.legend()


    def step(self, args):
        """Main stepping loop that tkinter periodically 
        accesses every "interval" milliseconds. "root" must
        be the Tkinter widget representing the root. """

        # capture arguments
        root = args[0]
        interval = args[1]


        # perform init if necessary
        if self.state[0] == 'init':
            self.init_graph()
            self.state[0] = 'run'


        elif self.state[0] == 'run':
            # update plot
            y = self.fake_get_data() #TODO: implement a real get data function
            self.update_plot(t=None, y_vectors=y)


        # return control to tkinter
        root.after(interval, self.step, (root,interval))

    def close(self):
        """Gracefully closes the backend acoustics RX thread."""
        self.exit_flg.set()


def main():
    # grab classes
    acoustics = Acoustics()
    gui = TkManager()

    # init the gui
    gui.init()

    # generate a figure for plotting
    f = Figure(figsize=(.1, .1), dpi=50)
    acoustics.attach_mpl_figure(f)

    # add matplotlib figure to gui
    gui.attach_mpl(f)
    def animate(i):
        #print "[animate]: " + str(i)
        pass #the invokation of this function alone forces the plot to update
    ani = animation.FuncAnimation(f, animate, np.arange(1, 200), interval=HZ60, blit=False)


    # Attach acoustics main loop and start running it.
    TK_MAINPROCESS_EXEC_TIME = 15
    gui.attach_thread(acoustics.step, TK_MAINPROCESS_EXEC_TIME)
    acoustics.start()

    # complete formatting and show the gui
    try:
        gui.auto_populate()
        gui.run()
    finally:
        acoustics.close()


if __name__ == '__main__':
    main()
