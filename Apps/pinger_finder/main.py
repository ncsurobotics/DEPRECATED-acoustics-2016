import ADC
import os
import numpy as np

# Python file
import watch_for_dead_bits
import ADS7865_Sampler
from LTC1564 import LTC1564
import trackPinger
import visFFT

help_text = """quit: quit the program.
help: display this help text."""


# 1. #####################################
##################### Main Sequence ######
##########################################

def main():
    # Display title sequence
    title()

    # Bring up user interface
    UI()

    # User is finished. Print Closing sequence
    exit_app()


# 2. #####################################
##################### Host Menu  ######
##########################################

def UI():

    # Important parameters
    Signal_Data = {'y': []}
    plt = None

    # Generate location expressions
    HOME = "HOME"
    ADC_APP = "ADC_APP"
    ADC_CONF = "CONFIG"
    loc = Location(HOME)

    # Print introductory text
    response(loc.curr, "Welcome! Please, type in a command:")

    q = 0
    ADC_active = False
    LTC_active = False

    while(q == 0):
        # build status variables

        # query user for input
        user_input = query(loc.path)

        # Log user response
        pass

        # a ############################
        ###### Global Command class ####
        ################################

        # respond to user input
        if ('quit' == user_input) or ('q' == user_input):
            q = 1

        elif ('help' == user_input) or ('h' == user_input):
            print('-' * 50)
            usage()
            print('-' * 50)

        # b ############################
        ########### ADC cmd Class ######
        ################################

        elif ('adc_status' == user_input) or ('s' == user_input):
            if ADC_active:
                ADS7865.ADC_Status()
            else:
                response(loc.curr, "Please run 'load_adc_app' first")

        elif ('load_adc_app' == user_input) or ('l' == user_input):
            ADC_active = True
            ADC_app_splash()
            loc.push(ADC_APP)
            response(loc.curr, "Loading ADC app...")
            ADS7865 = ADC.ADS7865()
            response(loc.curr, "Done loading app. Entering environment...")

        elif ('unload_adc_app' == user_input) or ('u' == user_input):
            response(loc.curr, "Closing app...")
            ADS7865.Close()
            loc.pop()

        elif ('adc_debug_wizard' == user_input) or ('d' == user_input):
            if ADC_active:
                adc_debug_wizard(ADS7865)
            else:
                response(loc.curr, "Please run 'load_adc_app' first")

        elif ('adc_collect_data' == user_input) or ('data' == user_input):
            if ADC_active:
                Signal_Data['y'] = ADS7865_Sampler.main(ADS7865, plt)
            else:
                response(loc.curr, "Please run 'load_adc_app' first")

        elif ('adc_conf' == user_input) or ('o' == user_input):
            loc.push(ADC_CONF)
            adc_config(ADS7865, loc)
            loc.pop()

        elif ("adc_analysis" == user_input) or ('a' == user_input):
            if ADC_active:
                adc_analysis_wizard(ADS7865, Signal_Data, plt)
            else:
                response(loc.curr, "Please run 'load_adc_app' first")
        # c ############################
        ########### Filter cmd Class ##
        ################################
        elif ("lf" == user_input) or ("load_filts" == user_input):
            LTC = LTC1564()
            LTC_active = True

        elif ("Glf" == user_input) or ("conf_G" == user_input):
            if LTC_active:
                print("Config Input Gain: enter a mode from 0 to 3")
                mode = eval(raw_input(">> "))
                LTC.GainMode(mode)
            else:
                response(loc.curr, "Please run 'lf' (load_filts) first")

        elif ("Flf" == user_input) or ("conf_F" == user_input):
            if LTC_active:
                print("Config Input Fc: enter a mode from 0 to 1")
                mode = eval(raw_input(">> "))
                LTC.FiltMode(mode)
            else:
                response(loc.curr, "Please run 'lf' (load_filts) first")

        # c ############################
        ########### utility cmd Class ##
        ################################

        elif ('plot_en' == user_input) or ('p' == user_input):
            plt = load_matplotlib()

        elif 'EOF' == user_input:
            response(loc.curr, "End of input file reached")

        else:
            response(loc.curr, "Not a recognized command! Try again.")
            usage()

# 3. #####################################
########### ADC function repository ######
##########################################


def adc_debug_wizard(ADC_object):
    keys = ['watch_for_dead_bits',
            'read_DBus',
            'check_DBus',
            'dummy_read_seq',
            'dummy_read_dac',
            'read_seq',
            'read_dac',
            'q']

    q = 0
    while (q != 1):
        # Print status
        print("current status:")
        ADC_object.ADC_Status()
        print("")

        # Print debug options
        print("enter one of the following debugging commands")
        printDebugs(keys)
        print("")

        # Take user input
        user_input = query('adc_debug_wizard')

        # route user
        if 'q' == user_input:
            q = 1
        elif ('watch_for_dead_bits' == user_input) or ('1' == user_input):
            watch_for_dead_bits.main(ADC_object)

        elif('3' == user_input):  # check_DBus
            temp = ADC_object.DBus.readStr()
            print("debug_wizard: DBus = %s" % temp)

        elif('6' == user_input):
            ADC_object.Read_Seq()

        elif ('7' == user_input):
            ADC_object.Read_Dac()


def printDebugs(keys):
    row = 1
    for key in keys:
        print("\t%d: %s" % (row, key))
        row += 1


def adc_config(ADC_OBJ, loc):
    # setup environment
    response(loc.curr, "You have entered the ADC config mode")
    q = 0

    # Get user's sample length
    response(loc.curr, "Please enter a sample length")
    SL = query(loc.curr)
    ADC_OBJ.sampleLength = int(eval(SL))

    # Get user's conversion rate
    response(loc.curr, "Please enter a sample rate")
    SR = query(loc.curr)
    ADC_OBJ.Update_SR(eval(SR))

    # Get user's threshold value
    response(loc.curr, "Please enter a threshold value (Volts)")
    THR = query(loc.curr)
    ADC_OBJ.threshold = eval(THR)

    # Get user's config
    ADC_OBJ.EZConfig()  # Empty argument means to use a wizard like this one

    # exit environment
    response(loc.curr, "Exiting ADC config mode")


def adc_analysis_wizard(ADC_OBJ, Signal_Data, plt):
    keys = ['noise_analysis', 'track_pinger', 'live_fft']

    q = 0
    while (q != 1):

        # Print debug options
        print("enter one of the following analysis commands")
        printDebugs(keys)
        print("")

        # Take user input
        user_input = query('adc_analysis_wizard')

        # route user
        if 'q' == user_input:
            q = 1
        elif 's' == user_input:
            # Print status
            print("current status:")
            ADC_OBJ.ADC_Status()
            print("")

        elif ('noise_analysis' == user_input) or ('1' == user_input):
            adc_noise_analysis(ADC_OBJ, Signal_Data, plt)
        elif ('track_pinger' == user_input) or ('2' == user_input):
            trackPinger.main(ADC_OBJ, plt)
        elif ('live_fft' == user_input) or ('3' == user_input):
            visFFT.main(ADC_OBJ, plt)


def adc_noise_analysis(ADC_OBJ, Signal_Data, plt=None):
    # Ask user to select a channel of data for analysis
    ADC_OBJ.ADC_Status()
    channel_sel = eval(raw_input("Please enter a channel (0 thru 3) for analysis: "))
    y = Signal_Data['y'][channel_sel]

    # Ask user to make sure that channel has no VLF components
    print("Please understand that the presense of VLF components on the "
          + "Channel will make this measurement inaccurate. Having a DC Component "
            + "is okay though.")

    # Null the DC component
    y = y - np.average(y)

    # Get T
    Ts = 1 / ADC_OBJ.convRate
    T = y.size * Ts

    # Compute Noise RMS
    i = 0
    Vnrms_sq = 0

    for samp in y:
        Vnrms_sq += 1 / T * samp**2 * Ts
    print("You got %f VoltsRMS noise here." % np.sqrt(Vnrms_sq))

    # plot if user has imported matplot lib
    if plt:
        (n, bins, patches) = plt.hist(y, 50, normed=1, histtype='bar')
        plt.title('Distribuition of error amongst %s samples' % y.size)
        plt.xlabel("error (volts)")
        plt.show()


# 4. #####################################
##################### Elements ###########
##########################################

def title():
    bar = '-' * 50

    print(bar)
    print(" " * 15 + " PINGER FINDER")
    print(bar)


def load_matplotlib():
    print("Loading Matplotlib library...")
    import matplotlib
    matplotlib.use('GTK')
    import matplotlib.pyplot as plt
    plt.ion()
    plt.hold(False)
    plt.close()
    print("...done.")

    return plt


def exit_app():
    print("Goodbye!")


def ADC_app_splash():
    bar = '- ' * 15
    os.system("clear")
    print(bar)
    print('v-' * 15)


def usage():
    text = ["  (h)elp: Get help.\n",
            "  (q)uit: quit this program.\n",
            "  (p)lot_en: enable plotting (needs X11 port forwarding).\n",
            "  (l)oad_adc_app: Startup the adc enviroment.\n",
            "  adc_(s)tatus: prints data regarding the adc.\n",
            "  (u)nload_adc_app: Close adc environment.\n",
            "  adc_c(o)nf: Change Settings of the ADC.\n",
            "  adc_(d)ebugger: debug the ADC.\n",
            "  adc_(a)nalysis: Grab some experimental data."]
    print('\n'.join(text))


class Location():

    def __init__(self, init):
        self.list = [init]
        self.refresh()

    def push(self, new_loc):
        """push: method for updating the loc object with
        new_loc, a string"""
        (self.list).append(new_loc)
        self.refresh()

    def pop(self):
        """pop: method for stepping back a location."""
        self.list.pop()
        self.refresh()

    def refresh(self):
        """refresh: method for updating several attribute of this
        class. primarily designed for internal use."""
        self.curr = self.list[-1]
        self.path = '>'.join(self.list)


def response(loc, s):
    """response: a means of generating a system response.
    Takes a string s and outputs it with the current location in
    the program, as designated by the string loc."""
    print('\n' + loc + ": " + s)


def query(loc):
    """query: a means of getting user input.
    This function Takes a string loc and uses it to inform the user
    where he is located while the being asked for his input."""

    request = raw_input("{%s} >>" % loc)

    return request

if __name__ == '__main__':
    main()
