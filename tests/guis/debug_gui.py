import time
import threading
import socket
import struct

from Tkinter import Tk, BOTH, TOP, RIGHT, LEFT
from ttk import Frame, Button, Style
import ttk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.animation as animation

from numpy import arange, sin, pi
import numpy as np

class SubFrame(Frame):
    """The main object for placing stuff in the GUI. It's treated as a
    section object, whereby we can divide up the window into sections."""

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

    def add_label(self, text, loc):
    	"""adds some label text in the desired location"""

    	label = ttk.Label(self.parent, text=text)
    	label.place(x=loc[0], y=loc[1])
        #self.pack(side=LEFT, fill=BOTH, expand=1)

    def add_button(self, name, func, loc, **kwargs):
        """Adds a button in the desired location of the SubFrame"""

        # set title of button
        print(func,kwargs)
        button = Button(self, text=name, command=func, **kwargs)

        # place the button
        button.place(x=loc[0], y=loc[1])
        #self.pack(side=LEFT, fill=BOTH, expand=1)

    def add_entry_box(self, loc, header=None):
        # get entry box parameters
        x1 = loc[0]
        y1 = loc[1]

        # place entry box
        entry = ttk.Entry(self)
        entry.place(x=x1, y=y1)

        # if specified, put a header above the entry box
        if header is not None:
            x2 = x1
            y2 = y1 - 20

            self.add_label(header, [x2,y2])

        # return the entry box for future get() commands
        return entry

    def commit(self, side=LEFT):
    	self.pack(side=side, fill=BOTH, expand=1)


class TkManager():
    """Wrapper for using TKinter to make an acoustics gui"""

    def __init__(self):
        self.root = Tk()
        self.style = None

        # panel #1: the buttons
        self.button_frame = None
        self.user_entry_field = None

        # panel #2: the plotter.
        self.mpl_canvas = None

    def init(self):
        # create a window
        self.place_window(WINDOW_WIDTH, WINDOW_HEIGHT)

        # set name of the window
        self.root.title = ("Quit")

        # stylize everything
        self.style = Style()
        self.style.theme_use('clam')

    def run(self):
        """Executes the main loop/thread containing the GUI"""
        self.root.mainloop()

    def auto_populate(self, acoustics_connect_func, acoustics_drytest_func, acoustics_send_func):
        """automatically does the layout stuff for this program"""
        # create a button frame object
        self.button_frame = SubFrame(self.root)
        button_frame = self.button_frame

        # Add buttons to the GUI
        button_frame.add_label('Acoustics Interface', [0,0])
        button_frame.add_button('Connect to acoustics', acoustics_connect_func, [5, 20])
        button_frame.add_button('test acoustics', acoustics_drytest_func, [5, 60])
        button_frame.add_button('quit', button_frame.quit, [5, 100], width=4)
        self.user_entry_field = button_frame.add_entry_box([5,160], "debug")
        button_frame.add_button("send", acoustics_send_func, [50, 100])

        # pack up the frame
        button_frame.commit()


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

    def getRoot(self):
        """Return the root object for this GUI"""
        return self.root

    def get_debug_cmd(self):
        
        field = self.user_entry_field
        if field is not None:
            return field.get()
        else:
            print("debug field does not exist!")
            return None

    def attach_mpl(self, mpl_figure):
        self.mpl_canvas = FigureCanvasTkAgg(mpl_figure, master=self.root)

    def attach_subprocess(self, func, exec_interval):
        """attaches a subprocess that will run in between GUI updates.
        args:
          * func: function that will be execututed after exec_interval seconds.
          * exec_interval: the length of the delay (in milliseconds) before func 
          executes
          
        as a tip, one should attach a basic "step" function that focuses on
        being the link between the GUI's graphics, and some other backend process
        collecting data'"""
        self.root.after(exec_interval, func, (self, exec_interval))

    def attach_thread(self, func, waittime):
        self.root.after(waittime, func, (self.root, waittime))
