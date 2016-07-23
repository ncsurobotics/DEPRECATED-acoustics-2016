#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable=too-many-ancestors
# pylint: disable=invalid-variable-name

"""
This program provideds a gui for connecting to
the BBB acoustics systems via ethernet.
"""
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

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 200

HZ60 = 16


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

    def commit(self):
    	self.pack(side=LEFT, fill=BOTH, expand=1)


class TkManager():

    def __init__(self):
        self.root = Tk()
        self.style = None

        # object placeholder
        self.mpl_canvas = None
        self.button_frame = None
        self.user_entry_field = None

    def init(self):
        # create a window
        self.place_window(WINDOW_WIDTH, WINDOW_HEIGHT)

        # set name of the window
        self.root.title = ("Quit")

        # stylize everything
        self.style = Style()
        self.style.theme_use('clam')

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

    def run(self):
        self.root.mainloop()

    def getRoot(self):
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

    def attach_thread(self, func, waittime):
        self.root.after(waittime, func, (self.root, waittime))



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

        # networking variables
        self.network = {}
        self.network['sock'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.network['IP'] = '152.1.150.32'
        self.network['portn'] = 22022
        self.network['sock'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.network['connected'] = False
        #self.conn = None
        
        # gui stuff
        self.gui = None


        # fake data parameters
        self.fake_data_rate = 1000.0 #hz

        # data attribute
        self.counter = 0

        # acoustics handles
        self.data_channels = ['CHA0', 'CHA1', 'CHB0', 'CHB1']

    def connect(self):
        """Connect to the beaglebone via a TCP connection"""

        # attain network parameters
        IP = self.network['IP']
        port = self.network['portn']

        print "connecting"
        #self.conn = self.network['sock'].connect((IP, port))
        self.network['sock'].connect((IP, port)) #^^ connection is implied for clients
        self.set_conn_status(True)

        print "connection successful"

    def is_connected(self):
        return self.network['connected']

    def send(self, msg):
        if self.is_connected():
            sock = self.network['sock']
            sock.send(msg)
        else:
            print("network not connected!!! Can't send msg.")

    def set_conn_status(self, status):
        """returns true if connection to acoustics system has been established."""
        self.network['connected'] = status

    def getsend_debug(self):
        """scripted cmd to pull a message out of the gui's text box, and
        send it to the beaglebone black"""
        msg = self.gui.get_debug_cmd()
        if msg is not None:
            self.send(msg)
        else:
            print "No message to Send?!"

    def drytest(self):
        # signal rx_thread that real data is going to come in
        self.state[0] = 'test-1'

        # send cmds to acoustics that start the drytest
        self.send('stream') # cmd to start the stream



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

    def attach_gui(self, root):
        """Takes "root" as a reference to the TKinter layout manager
        defined in this same file. """
        self.gui = root

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
                self.lines[i].set_data(t,y_vectors[i])
            
            self.axes.set_xlim([0, t[-1]])
            self.axes.set_ylim([-2.5, 2.5])
            return

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
            self.state[0] = 'demo'


        elif self.state[0] == 'demo':
            # update plot
            y = self.fake_get_data()
            self.update_plot(t=None, y_vectors=y)

        elif self.state[0] == 'test-1':
            print "in test-1"
            # issue get data command
            self.send('get data')
            #import pdb; pdb.set_trace()

            # update state
            self.state[0] = 'test-2'

        elif self.state[0] == 'test-2':
            print "in test-2"
            recv = self.network['sock'].recv

            # receive packet size
            n_ch = eval( recv(128) )
            n_point = eval( recv(128) )
            
            y = []
            for ch in range(n_ch):
                # ping server
                self.network['sock'].send('o')
                print 'ping'

                # receive data
                n_byte = struct.calcsize('f'*n_point)
                data = struct.unpack('f'*n_point, recv(n_byte))
                y.append(data)
                
            # update the plot
            self.update_plot(t=range(n_point), y_vectors=y)

            # update user
            print("%d points" % n_point)

            # update state
            self.state[0] = 'test-1'



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

    # attach gui to acoustics module
    acoustics.attach_gui(gui)

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
        gui.auto_populate(acoustics.connect, 
            acoustics.drytest,
            acoustics.getsend_debug)
        gui.run()
    finally:
        acoustics.close()


if __name__ == '__main__':
    main()
