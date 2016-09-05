
import sys
sys.path.insert(0, '../../host_communication/')

import numpy as np
from numpy.fft import fft

import gui_lib
import acoustics_sim as acoustics
from acoustics_terminal2 import API

ACOUSTICS_DATA_DIR = '/home/josh/Documents/URC-development/Raw_Footage/acoustics/'

class Main_Window(gui_lib.Window):
    def __init__(self, gui, parent, x, y):
        print "REMEMBER: NEXT IMMEDIATE GOAL IS TO MAKE ACOUSTICS.PY WORK."
        super(Main_Window,self).__init__(parent, 'main')
        self.gui = gui


        # setup parameters for the window
        self.w = 150
        self.h = 50

        # place the window in a convenient location
        self.place(self.w, self.h, x, y)

        # place title & buttons
        self.pack_text('Acoustics')
        self.pack_button('Select Mission', callback=self.open_mission_window)

        # child window variables
        self.mission_window = None

    def open_mission_window(self):
        self.gui.create_window('mission')

        self.mission_window = Mission_Window(self.gui.get_window('mission'),150,40)

        # import data into mission window
        fp = self.gui.open_file( ACOUSTICS_DATA_DIR )
        self.mission_window.import_data( fp )

        # upload data to the window

        self.mission_window.auto_populate(self.mission_window.data, 0)


class Mission_Window(gui_lib.Window):
    def __init__(self, parent, x, y):
        super(Mission_Window,self).__init__(parent, 'mission')

        # setup parameters for the window
        self.w = 600
        self.h = 650

        # place the window in a convenient location
        self.place(self.w, self.h, x, y)

        # place grided frames
        #self.create_frame('plot pane', idx=(0,0))
        self.create_frame('time1', idx=(1,0), frame_type='plot', shape=(2.5,2), ylim=(-2.6, 2.6))
        self.create_frame('fft1', idx=(2,0), frame_type='plot', shape=(2.5,0.5), ylim=(0,100), xlim=(0,40e3), xticks=[25e3, 30e3, 35e3, 40e3])
        self.create_frame('time2', idx=(3,0), frame_type='plot', shape=(2.5,2), ylim=(-2.6, 2.6))
        self.create_frame('fft2', idx=(4,0), frame_type='plot', shape=(2.5,0.5), ylim=(0,100), xlim=(0,40e3), xticks=[25e3, 30e3, 35e3, 40e3])


        #self.create_frame('feedback pane', idx=(0,1))
        #self.insert_frame('compass', 'feedback pane', idx=(0,0), frame_type='plot', shape=(2.5,2))

        # add buttons for stepping through data
        self.create_frame('navigation', idx=(0,0))
        self.insert_button('left', frame_name='navigation', side='left', callback=self.prev_sample)
        self.insert_button('right', frame_name='navigation', side='left', callback=self.next_sample)

        # add buttons for manipulatings processing
        self.insert_checkbutton('adaptive_gain', frame_name='navigation', side='top', varname='tog_gain', stick='w', default=True, callback=self.refresh)
        self.insert_checkbutton('zoomY', frame_name='navigation', side='top', varname='zoomY', stick='w', callback=self.refresh)
        self.insert_checkbutton('zoomX', frame_name='navigation', side='top', varname='zoomX', stick='w', callback=self.refresh)

        # add buttons for manipulatings processing
        #TODO: Empty plots when turning off replay mode.
        #TODO: code live mode using acoustics terminal API
        #TODO: code simulated adc in acoustics_terminal.py
        # Replay mode: Replay acoustics data from previously recorded acoustics data
        # Live mode: stream acoustics data the main process algorithm. A.k.a. simulate acoustics.
        self.create_frame('navigation2', idx=(0,1))
        self.insert_checkbutton('Replay Mode', frame_name='navigation2', side='top', varname='replay_mode', stick='w', default=True, callback=self.refresh)
        self.insert_checkbutton('Live Mode', frame_name='navigation2', side='top', varname='live_mode', stick='w', callback=self.refresh)
        #self.insert_checkbutton('Simulation Mode (Stream)', frame_name='navigation2', side='top', varname='zoomX', stick='w', callback=self.refresh)

        # add pane for reviewing data
        self.create_frame('info', idx=(1,1))
        self.insert_dynamiclabel('Heading (reported)', frame_name='info', idx=(0,0), side='top', stick='e', units='deg')
        self.insert_dynamiclabel('Gain Applied', frame_name='info', idx=(1,0), side='top', stick='e', units='V/V')
        self.insert_dynamiclabel('Input Signal Strength (ch1)', frame_name='info', idx=(2,0), side='top', stick='e', units='dBm')

        # init plots
        self.data = acoustics.Data()
        self.sample_num = None

        # simulator placeholders
        self.terminal = None


    def refresh(self):
        # Check if zoom option is enabled
        zoomY = self.get_checkbutton_status('navigation', 'zoomY')
        if zoomY:
            self.mpl_data['time1']['axes'].set_ylim(-0.3,0.3)
            self.mpl_data['time2']['axes'].set_ylim(-0.3,0.3)
        else:
            self.mpl_data['time1']['axes'].set_ylim(-2.6,2.6)
            self.mpl_data['time2']['axes'].set_ylim(-2.6,2.6)

        # update all the plots and graphics
        self.auto_populate(self.data, self.sample_num)

        # simulate results if applicable
        if self.get_checkbutton_status('navigation2', 'live_mode') == True:
            self.update_sim(self.data, self.sample_num) #TODO: make this function better
        else:
            pass # empty the sim box
            
    def update_sim(self, data, idx):
        # check if sim is initialized
        if self.terminal == None:
            self.terminal = API()

        idx = self.sample_num
        sample = data.get_data()

        # time domain data
        start   = sample['start'][idx]
        end     = sample['end'][idx]
        M       = end-start
        dt      = 1.0/sample['sample rate'][idx]  #sample[]
        t       = np.arange(0, M*dt, dt)
        gain    = sample['AGain'][idx] * sample['DGain'][idx]

        sim_data = self.terminal.process( sample['input'][start:end,0:4] )

    
    def next_sample(self):
        self.sample_num += 1
        self.refresh()


    def prev_sample(self):
        self.sample_num -= 1
        self.refresh()

    def import_data(self, fp):
        self.data.import_file(fp)
        self.auto_populate(self.data, 0)


    def auto_populate(self, data, idx):
        print self.get_checkbutton_status('navigation', 'tog_gain')
        self.sample_num = idx
        sample = data.get_data()

        # time domain data
        start   = sample['start'][idx]
        end     = sample['end'][idx]
        M       = end-start
        dt      = 1.0/sample['sample rate'][idx]  #sample[]
        t       = np.arange(0, M*dt, dt)
        gain    = sample['AGain'][idx] * sample['DGain'][idx]

        #TODO: add legends to plot

        if self.get_checkbutton_status('navigation', 'tog_gain') == True:
            y1 = sample['input'][start:end,0]
            y2 = sample['input'][start:end,1]
            y3 = sample['input'][start:end,2]
            y4 = sample['input'][start:end,3]
        else:
            
            y1 = sample['input'][start:end,0] / gain
            y2 = sample['input'][start:end,1] / gain
            y3 = sample['input'][start:end,2] / gain
            y4 = sample['input'][start:end,3] / gain


        self.plot('time1', y1, t, trace=0, name=sample['mapping'][0])
        self.plot('time1', y2, t, trace=1, name=sample['mapping'][1])

        self.plot('time2', y3, t, trace=0, name=sample['mapping'][2])
        self.plot('time2', y4, t, trace=1, name=sample['mapping'][3])

        # frequency domain data
        fs = sample['sample rate'][idx]
        df = fs / M
        f = np.arange(0, M*df, df)

        #import pdb; pdb.set_trace()
        Y1 = abs(fft(y1))
        Y2 = abs(fft(y2))
        Y3 = abs(fft(y3))
        Y4 = abs(fft(y4))

        # Make FFT plots show frequency information
        self.plot('fft1', Y1, f, trace=0)
        self.plot('fft1', Y2, f, trace=1)
        self.plot('fft2', Y3, f, trace=0)
        self.plot('fft2', Y4, f, trace=1)

        #TODO: print heading info on the gui
        heading = sample['ping_loc'][idx]
        if type(heading) != type(''):
            self.update_label('info', 'Heading (reported)', "{:.1f}".format(heading))
        else:
            self.update_label('info', 'Heading (reported)',' ---')

        # print gain info
        self.update_label('info', 'Gain Applied', "{:.1f}".format(gain))

        sig_strength = acoustics.ADC_Tools.meas_vpp(y1 / gain)
        sig_strength = np.log10(sig_strength*sig_strength/50.0*1000)*10
        self.update_label('info', 'Input Signal Strength (ch1)', "{:.1f}".format(sig_strength))

    def plot(self, frame_name, y, x, trace=None, name=None):
        # collect mpl data
        mpl_data = self.get_mpl_data(frame_name)
        axes = mpl_data['axes']
        canvas = mpl_data['canvas']


        try:
            line = axes.lines[trace]
            line.set_ydata(y)

        except IndexError:
            if trace==0 or len(axes.lines)==trace:
                axes.plot(x, y, label=name)
            else:
                IndexError("Invalid trace selection: trace{}".format(trace))

            # add to legend
            if name is not None:
                axes.legend()

        # draw the update
        canvas.draw()

def access_terminal_api(self):
    # TODO: code the check box detection

    # TODO: Code for adding for api stuff before polotting the info
    pass


def main():
    # instantiate major objects
    gui = gui_lib.TK_Framework()

    # create the main window
    main_window = Main_Window(gui, gui.get_window('main'),20,40)
    
    # create the mission window
    #import pdb; pdb.set_trace()
    #gui.create_window('mission')
    #mission_window = Mission_Window(gui.get_window('mission'),150,40)
    #mission_window.import_data( gui.open_file() )
    
    
    gui.get_root().mainloop()
    # let user select a data file

main()