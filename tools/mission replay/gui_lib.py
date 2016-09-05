import Tkinter
from Tkinter import Tk, Toplevel, BooleanVar
from ttk import Style
from ttk import Button, Checkbutton, Entry, Frame
from ttk import Label, LabelFrame, Menubutton 
from ttk import PanedWindow, Radiobutton, Scale
from tkFileDialog import askopenfilename

import matplotlib
matplotlib.use("TkAgg")
matplotlib.rc('font', size=6)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

class TK_Framework(object):
    def __init__(self):
        self.root = Tk()

        # list of open windows
        self.windows = {'main':self.root}

        # setup the overall style of the gui
        self.style = Style()
        self.style.theme_use('clam')

    def get_window(self,name):
        return self.windows[name]

    def create_window(self, name):
        self.windows[name] = Toplevel()
    
    
    @staticmethod
    def open_file(init_dir):
        filename = askopenfilename(initialdir=init_dir)
        return filename

    def hide_root(self):
        """Hides the root window"""
        self.root.withdraw()

    def get_root(self):
        return self.root

class Window(object):
    def __init__(self, window, name=''):
        self.window = window
        self.name = name

        # window content variables
        self.frames = {}
        self.frame_data = {}
        self.mpl_data = {}
        self.checkbuttons = {}
        self.dynamiclabels = {}

        # window parameters
        self.w = None
        self.h = None
        self.x = None
        self.y = None

        # tk wrappers
        self.TkSide = {'left':Tkinter.LEFT,
                       'right':Tkinter.RIGHT,
                       'top':Tkinter.TOP,
                       'bottom':Tkinter.BOTTOM,}
        
        # create a new window
        #self.window = Toplevel(self.window)
    
    def set_name(self, name):
        """Changes the name of a window"""
        self.name = name

        #TODO: Make this actually change the title of a window

    def create_frame(self, name, idx, frame_type=None, **kwargs):
        """Creates a gridded frame inside the window.
        ARGS:
          * name: name of the frame
          * idx: tuple containing the (r,c) designation of the frame
          within the grid. r=row. c=column."""
        # create the frame
        frame = Frame(self.window)

        # add frame to list of frames
        self.frames[name] = frame

        # pre-fill the frame
        if frame_type is None:
            pass
        elif frame_type == 'plot':
            # determine initialization variables
            dim = kwargs.get('shape', None)
            ylim = kwargs.get('ylim', None)
            xlim = kwargs.get('xlim', None)
            xticks = kwargs.get('xticks', None)

            # generate the figure
            f = Figure(figsize=dim, dpi=113  )
            a = f.add_subplot(111)

            # generate canvas
            canvas = FigureCanvasTkAgg(f, master=frame)

            # set axes ticks
            if ylim is not None:
                a.set_ylim(*ylim)

            if xlim is not None:
                a.set_xlim(*xlim)

            if xticks is not None:
                a.set_xticks(xticks)

            # Commit the canvas to the gui
            canvas.get_tk_widget().pack()

            # save canvas data for later access
            self.mpl_data[name] = {'axes':a,
                                   'figure':f,
                                   'canvas':canvas}
                                   
            self.frame_data['plot'] = {'mpl_canvas':canvas}

        # commit the frame to workspace
        frame.grid(row=idx[0], column=idx[1])

    def get_mpl_data(self, frame_name):
        return self.mpl_data[frame_name]

    def insert_frame(self, name, parent_frame_name, idx, frame_type=None, **kwargs):
        parent_frame = self.frames[parent_frame_name]
        frame = Frame(parent_frame)

        # add frame to list of frames
        self.frames[name] = frame

        # pre-fill the frame
        if frame_type is None:
            pass
        elif frame_type == 'plot':
            # generate canvas
            dim = kwargs['shape']
            f = Figure(figsize=dim, dpi=113  )
            a = f.add_subplot(111)
            canvas = FigureCanvasTkAgg(f, master=frame)
            
            # Commit the canvas to the gui
            canvas.get_tk_widget().pack()

            # save canvas data for later access
            self.mpl_data[name] = {}
            self.frame_data['plot'] = {'mpl_canvas':canvas}

        # commit the frame to workspace
        frame.grid(row=idx[0], column=idx[1])


    def place(self, w, h, x, y):
        """Places the window wherever. Might as well be 
        called 'resize' sometimes."""
        self.w = w
        self.h = h
        self.x = x
        self.y = y

        # commits geometry in the window
        self.window.geometry('{}x{}+{}+{}'.format(w, h, x, y))

    
    def get_origin(self):
        return (self.x, self.y)

    def set_size(self, w, h):
        """Places the window in the top left corner of screen.
        User may specify dimensions."""
        w = str(w)
        h = str(h)
        dim = w + 'x' + h

        x = str(self.x)
        y = str(self.y)
        self.window.geometry('{}x{}+{}+{}'.format(w, h, x, y))

    def pack_text(self, text, frame=None):
    	"""adds some label text in the desired location"""

        if frame is None:
    	    label = Label(self.window, text=text)
        else:
            label = Label(frame, text=text)

        label.pack()

    def pack_button(self, text, callback=None):
        button = Button(self.window, text=text, command=callback)
        button.pack()

    def insert_button(self, text, frame_name, side, callback):

        frame = self.frames[frame_name]
        button = Button(frame, text=text, command=callback)

        button.pack(side=self.TkSide[side])

    def insert_checkbutton(self, text, frame_name, side, varname, stick=None, default=None, callback=None):
        """Inserts a check button widget in the specified frame.
        ARGS:
          * var: a TKinter supported variable, such as IntVar(), StrVar(),
          and etc."""

        # create a variable for this task
        var = BooleanVar()
        if default is not None:
            var.set(default)

        # create the widget
        frame = self.frames[frame_name]
        check = Checkbutton(frame, text=text, variable=var, command=callback)
        check.pack(side=self.TkSide[side], anchor=stick)

        # save data regarding the widget
        if self.checkbuttons.get(frame_name, None) == None:
            self.checkbuttons[frame_name] = {}

        self.checkbuttons[frame_name][varname] = {'button':check,
                                                  'var':var}

    def insert_dynamiclabel(self, header, frame_name, idx, **kwargs):
        side    = kwargs.get('side',None) 
        stick   = kwargs.get('stick', None) 
        unit    = kwargs.get('units', None)
        frame   = self.frames[frame_name]

        # pack info
        label1 = Label(frame, text=header+': ', )
        label2 = Label(frame, text='---'+unit)

        label1.grid(row=idx[0], column=idx[1], sticky=stick)
        label2.grid(row=idx[0], column=idx[1]+1, sticky=stick)

        # save data regarding the widget
        if self.dynamiclabels.get(frame_name, None) == None:
            self.dynamiclabels[frame_name] = {}

        self.dynamiclabels[frame_name][header] = label2

    def update_label(self, frame_name, label_name, value): 
        return self.dynamiclabels[frame_name][label_name].config(text=value)
    
    def get_checkbutton_status(self, frame_name, name):
        return self.checkbuttons[frame_name][name]['var'].get()
    
    def _generate_figure(self):
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
