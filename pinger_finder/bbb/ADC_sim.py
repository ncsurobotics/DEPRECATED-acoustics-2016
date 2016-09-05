
import numpy as np

## simply copy and paste the global variable section of ADC.py,
## but be sure to comment out anything regarding python paths.

# Global ADC program Constants
PRU0_DDR_MEM_OFFSET = 1
PRU0_SL_MEM_OFFSET = 2
PRU0_CR_Mem_Offset = 3
PRU0_DB_MEM_OFFSET = 4
PRU0_THR_Mem_Offset = 5
HC_CR = 0xBEBC200
F_CLK = 200e6

# commenting out python path stuff
###INIT0 = path.join(BIN_DIR, "init0.bin")
###INIT1 = path.join(BIN_DIR, "init1.bin")
###ADS7865_MasterPRU = path.join(BIN_DIR, "ADS7865_sample.bin")
###ADS7865_ClkAndSamplePRU = path.join(BIN_DIR, "pru1.bin")

WORD_SIZE = 12

BYTES_PER_SAMPLE = 4
MIN_SAMPLE_LENGTH = 2
DEFAULT_DAC_VOLTAGE = 2.49612  # volts
DEFAULT_THRESHOLD = 0  # volts
TOTAL_CHANNELS = 4
SAMPLES_PER_CONV = 2
STATUS_BLOCK = 1
TIMEOUT_STATUS_BIT = 2
DBOVF_BIT = 3
TFLG0_BIT = 4
TFLG1_BIT = 5

CONV_RATE_LIMIT = 800e3  # Hertz

PLUSMINUS = u'\xb1'.encode('utf-8')
DIFF_PAIR_1 = "CHA0" + PLUSMINUS
DIFF_PAIR_2 = "CHA1" + PLUSMINUS
DIFF_PAIR_3 = "CHB0" + PLUSMINUS
DIFF_PAIR_4 = "CHB1" + PLUSMINUS

CODE_READDAC = 0x103
CODE_SWRESET = 0x105
CODE_READSEQ = 0x106
CODE_WRITEDAC = 0x101

# Global Functions


class ADS7865(object):
    def __init__(self, sr=0.0, smp_len=0):
        """ Configures several BBB pins as necessary to hold the ADC in an idle state

        Args:
            cr: Conversion Rate (float)
            smp_len: Sample Length (integer)


        Parameters (in order of initialization):
            self.DBus
            self.WR
            self._RD
            self._CONVST
            self._CS
            self."ddr stuff"
            self.n_channels
            self.conversion_rate
            self.deadband_ms
            self.arm_status
            self.seq_desc
            self.ch
            self.delay
            self.digital_gain
            self.threshold
            self.corrected_threshold
            self.cr_specd
            self.modified
            self.sample_rate
            self.dac_voltage
            self.LSB
            self.TOF
            self.TRG_CH
            self.digital_gain
        """
        # Loads the BBB cape overlays that allow control of the PRUSS
        # and it's IO via pypruss. Note: pypruss will not work correctly
        # until this system level command is ran. Do not try to use the
        # pypruss library before running this command.
        ###boot.load()

        # GPIO Stuff
        ###self.DBus = Port(DB_pin_table)
        ###self.DBus.set_port_dir("in")

        ###self.WR = Port(WR_pin)
        ###self.WR.set_port_dir("out")
        ###self.WR.write_to_port(1)

        ###self._RD = Port(RD_pin)
        ###self._RD.set_port_dir("out")
        ###self._RD.write_to_port(1)

        ###self._CONVST = Port(CONVST_pin)
        ###self._CONVST.set_port_dir("out")
        ###self._CONVST.write_to_port(1)

        ###self._CS = Port(CS_pin)
        ###self._CS.set_port_dir("out")
        ###self._CS.write_to_port(0)

        # PRUSS Stuff
        ###self.ddr = {}
        ###self.ddr['addr'] = pypruss.ddr_addr()
        ###self.ddr['size'] = pypruss.ddr_size()
        ###self.ddr['start'] = 0x10000000
        ###self.ddr['filelen'] = self.ddr['size'] + 0x10000000
        ###self.ddr['offset'] = self.ddr['addr'] - 0x10000000
        ###self.ddr['end'] = 0x10000000 + self.ddr['size']

        msg = ("ADS7865: Allowing one 32bit memory block per sample, it is "
               "possible to collect {samp:.1f}K Samples in a single burst. These "
               "sample points are stored in DDRAM, which is found at the "
               "address range starting at {addr}")

        print(msg.format(
            #samp=self.ddr['size'] / 1000.0,
            samp=0,
            #addr=str(hex(self.ddr['addr'])))
            addr=str(hex(0)))
        )

        self.sampling_rate = sr
        self.deadband_ms = 0
        self.sample_length = int(smp_len)
        self.arm_status = "unknown"
        self.seq_desc = "unknown"
        self.ch = ['unknown'] * 4
        self.delay = [-99] * 4

        self.digital_gain = 1

        self.update_threshold(DEFAULT_THRESHOLD)
        self.sr_specd = 0  # parameter for keeping the up with the last spec
        self.modified = True
        self.sample_rate = None
        self.dac_voltage = DEFAULT_DAC_VOLTAGE
        self.lsb = self.dac_voltage / (2**(WORD_SIZE - 1))  # Volts

        # Loads overlays: For that will be later needed for
        # muxing pins from GPIO to pruout/pruin types and vice versa.
        self.sw_reset()

        # Any other variables that will later be relevent
        self.TOF = None
        self.TRG_CH = None
        self.y = None
        self.y = None


    def sim_load_data(self, input_data):
        self.y = input_data

    ############################
    #### GPIO Commands  #######
    ############################
    def config(self, cmd_list):
        """ Takes a list of hex values (cmd_list) and bitbangs the ADC
        accordingly. User may refer to the datasheet for an explanation
        of what the hex values actually mean. For examples of correct
        application, see: ez_config() method
        """

        # Callee save the port direction
        #callee_sPD = self.DBus.portDirection

        #
            
            
        for cmd in cmd_list:
            #self.WR.write_to_port(0)  # Open ADC's input Latch

            #self.DBus.set_port_dir("out")  # Latch open, safe to make DB pins an out
            #self.DBus.write_to_port(cmd)  # Write the value to the DB pins

            print('ADS7865: Databus cmd %s has been sent.' % hex(cmd))
            #self.WR.write_to_port(1)  # Latch down the input


    def ez_config(self, sel=None):
        """ Allows the user to access commonly used config command (presets).

        Args:
            sel: An integer from 0 to 5 representing a particular preset
        """

        # NOTES TO USER
        # --At powerup, sequencer_register=0x000
        # --Capturing one channel (non-pair) in isolation is doable by selecting sel=0
        # or sel=1 (since ADS7865 resets the data_output pointer at the beginning of every
        # CONVST), but the user must also take the extra precaution to disable the
        # "sub-sampling" portion of the PRUSS code in order for it to work.

        if sel is None:
            # Generate Query to user to see what kind of config he wants
            options = ["0a/0b differential channel pair",
                       "1a/1b differential channel pair",
                       "0a/0b differential channel pair w/ sequencer re-init",
                       "1a/1b differential channel pair w/ sequencer re-init",
                       "0a/0b -> 1a/1b in FIFO style",
                       "1a/1b -> 0a/0b in FIFO style"]

            print("Please select from one of the options below:")
            for i in range(len(options)):
                print("  %d: %s" % (i, options[i]))

            # Take input
            sel = eval(raw_input("Enter number here: "))

        # Single channel (pair) enable
        if sel == 0:
            # User has chosen to sample the 0a/0b differential channel pair.
            self.config([0x100])

            # Update statuses
            seq = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, '', '']
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 2

        elif sel == 1:
            # User has chosen to sample the 1a/1b differential channel pair.
            self.config([0xD00])

            # Update statuses
            seq = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, '', '']
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 2

        # Single channel (pair) enable with sequencer reinitialization
        elif sel == 2:
            # User has chosen to sample the 0a/0b differential channel pair
            # while disabling the sequencer register. NOTE: The reason why
            # this would ever be necessary is unclear, as it seems to have
            # the same functionality of ez_config 0.
            self.config([0x104, 0x000])

            # Update statuses
            seq = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, '', '']
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 2

        elif sel == 3:
            # User has chosen to sample the 1a/1b differential channel pair
            # while disabling the sequencer register NOTE: The reason why
            # this would ever be necessary is unclear, as it seems to have
            # the same functionality of ez_config 1.
            self.config([0x304, 0x000])

            # Update statuses
            seq = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, '', '']
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 2

        # Dual channel (pair) enable
        elif sel == 4:
            # User has chosen to sample the 0a/0b -> 1a/1b in FIFO style
            self.config([0x104, 0x230])

            # Update statuses
            seq1 = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            seq2 = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            seq = seq1 + " -> " + seq2
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, DIFF_PAIR_2, DIFF_PAIR_4]
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 4

        elif sel == 5:
            # User has chosen to sample the 1a/1b -> 0a/0b in FIFO style
            self.config([0x104, 0x2c0])

            # Update statuses
            seq1 = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            seq2 = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            seq = seq1 + " -> " + seq2
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, DIFF_PAIR_1, DIFF_PAIR_3]
            self.update_config_text(seq, chans)

            # Update n channels
            self.n_channels = 4

        if self.sr_specd:       # Last parameter that the user specd was SR
            self.update_sample_rate(self.sample_rate)
        else:
            conv_rate_warning()

    def update_delays(self):
        if self.n_channels == 2:
            self.delay = [0, 0]
        elif self.n_channels == 4:
            if self.conversion_rate != 0:
                delay = 1 / self.conversion_rate
            else:
                delay = None

            self.delay = [0, 0, delay, delay]
        else:
            raise IOError("%r is not a valid channel size." % self.n_channels)


    def preset(self, sel):
        """
        """

        if sel == 0:
            """Primary competition config. This is the goto place for
            determining the samplesize, sampling rate, # of simultaneous
            channels, and (initial) threshold value.
            """
            self.update_deadband_ms(0.5e3)
            self.set_sample_len(1e3)
            self.update_sample_rate(300e3)
            self.update_threshold(1)
            self.ez_config(4)
            
        elif sel == 1:
            """Secondary competition config. This is the goto place for
            determining the samplesize, sampling rate, # of simultaneous
            channels, and (initial) threshold value.
            """
            self.update_deadband_ms(1)
            self.set_sample_len(1e3)
            self.update_sample_rate(800e3)
            self.update_threshold(.1)
            self.ez_config(0)

        elif sel == 100:
            """
            Prototype (Test config #0)
            Date: Friday, May 8th

            Purpose: Anything

            General Considerations: This isn't as much a preset as much as
            it is a prototyping tool. Unlike other presets embedded in this
            function, the user is free to change the settings anytime as he
            sees fit. If something more "stable" is desirable, try another
            preset or make a new one."""
            self.update_deadband_ms(0)
            self.set_sample_len(1e3)
            self.update_sample_rate(300e3)
            self.update_threshold(.1)
            self.ez_config(0)
            
        elif sel == 101:
            """
            Test Config for Acoustics terminal
            Date: Wednesday, May 13

            Purpose: Faciliting tests on acoustics_terminal.py.

            General Considerations: Changes to this config are okay
            as long as they're for acoustics_terminal.py.
            """
            self.update_deadband_ms(0)
            self.set_sample_len(1e3)
            self.update_sample_rate(300e3)
            self.update_threshold(1)
            self.ez_config(4)

        elif sel == 102:
            """
            Test Config for echo measurements
            Date: June 16, 2015

            Purpose: Long recording for watching all signals over a
            long span of time in the acoustics_terminal app.
            """
            self.update_deadband_ms(1)
            self.set_sample_len(10e3)
            self.update_sample_rate(400e3)
            self.update_threshold(.5)
            self.ez_config(4)

        else:
            print("Unknown preset!")


    def update_deadband_ms(self, ms):
        print("ADS7865: Deadband length set to %dms" % int(ms))
        self.deadband_ms = ms
    
    def update_threshold(self, desired_threshold):
        # Save desired_threshold value
        self.threshold = desired_threshold

        # Compute & save corrected threshold
        self.corrected_threshold = desired_threshold / self.digital_gain

    def update_digital_gain(self, desired_gain):
        # save argument
        self.digital_gain = desired_gain

        # Update threshold attribute to adjust self.corrected_threshold
        # to a value respresenting the new digital gain value
        self.update_threshold(self.threshold)

    def set_sample_len(self, sl):
        """ Sets the sample length

        Args:
            sl: sample length
        """
        self.sample_length = int(sl)


    def sw_reset(self):
        """
        """

        print("Performing ADC device reset...")
        ###self.config([CODE_SWRESET])

        # Immediate parameters that get defined at reset
        self.n_channels = 2

        # DAC outputs the default voltage
        self.dac_voltage = DEFAULT_DAC_VOLTAGE
        self.lsb = self.dac_voltage / (2**(WORD_SIZE - 1))  # Volts

        # Update sequencer and channel descriptions
        self.seq_desc = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
        self.ch[0] = DIFF_PAIR_1
        self.ch[1] = DIFF_PAIR_3
        self.ch[2] = ''
        self.ch[3] = ''

        # Update other more complex parameters
        self.update_sample_rate(self.sampling_rate)

        # Update meta parameters
        self.modified = True

        # Let user know work is done
        print("... done.")

    def update_sample_rate(self, sr):
        """ Update the sample rate

        Args:
            sr: Sample rate
        """
        # Update modified bit
        self.modified = True

        # Update sampling rate
        self.sample_rate = float(sr)

        # Update sampling period
        if self.sample_rate != 0:
            self.sampling_period = 1 / self.sample_rate
        else:
            self.sampling_period = None

        # Update Conversion rate
        self.conversion_rate = self.sr_to_cr(sr)

        self.sr_specd = True

        if self.conversion_rate > CONV_RATE_LIMIT:
            print(
                "Your spec'd conversion rate"
                + " (%dKHz)" % (self.conversion_rate / 1000)
                + " exceeds the system's limit"
                + " (%dKHz)" % (CONV_RATE_LIMIT / 1000)
            )

        # Update delay config (dependent on conversion rate)
        self.update_delays()

    def sr_to_cr(self, sr):
        """
        """

        if self.n_channels != 0:
            return sr * (self.n_channels / float(SAMPLES_PER_CONV))
        else:
            print("self.n_channels == 0. Unable to compute a convRate!")
            return None

    ############################
    # General ADC Commands  #####
    ############################
    def update_config_text(self, seq, channels):
        """
        Takes the formatted strings seq and channels uses them to
        update internal parameters useful for printing out the
        config of the ADC.

        args:
            seq: string acting as a oneliner describing the ADC config.
            examples includes "CHA0+/CHB0+ -> CHA1+"/CH1+" or just
            "CHA0+/CHB0+"

            channels: list of string containing the same information
            embedded in seq, sans the "/" and "->" visual formatting
            stuff.
        """
        # Update human readable description
        self.seq_desc = seq

        # Update channel descriptions
        self.ch_idx = []
        for i in range(TOTAL_CHANNELS):
            self.ch[i] = channels[i]

            if self.ch[i] == DIFF_PAIR_1:
                self.ch_idx.append(1)
            elif self.ch[i] == DIFF_PAIR_2:
                self.ch_idx.append(2)
            elif self.ch[i] == DIFF_PAIR_3:
                self.ch_idx.append(3)
            elif self.ch[i] == DIFF_PAIR_4:
                self.ch_idx.append(4)
            elif self.ch[i] == '':
                pass  # Blank channel
            else:
                raise ValueError('ch "{0}" is an invalid '.format(channels[i])
                                 + "channel.")

    def update_delays(self):
        if self.n_channels == 2:
            self.delay = [0, 0]
        elif self.n_channels == 4:
            if self.conversion_rate != 0:
                delay = 1 / self.conversion_rate
            else:
                delay = None

            self.delay = [0, 0, delay, delay]
        else:
            raise IOError("%r is not a valid channel size." % self.n_channels)

    ############################
    #### PRUSS Commands  #######
    ############################
    def get_data(self):
        """Simplifies the process of getting data when it's requested. This
        method will typically replace any use of "self.burst()" and deciding
        whether or not you have to arm the ADC or not.
        """

        #y, TOF = self.burst()
        self.TOF    = False
        self.TRG_CH = 0
        y           = self.y
        TOF         = self.TOF
        
        if TOF == False:
            return y
        else:
            return None

    
class ADC_Tools(object):
    def meas_vpp(self, ADC):
        """Computes the vpp for each channel that the ADC is using.
        """
        # initialize variables
        vpp = []

        # Compute the vpp for each channel
        for ch in range(ADC.n_channels):
            vpp.append(np.amax(ADC.y[ch]) - np.amin(ADC.y[ch]))
        
        # Return tuple containing the data
        return tuple(vpp)

    def find_local_maxima(self, a):
        """
        args:
            y = array (numpy or list) of values
        """

        # Initial arrays and bits
        peaks = []
        rising_bit = 0

        for i in range(1, a.size):
            prev_value = a[i - 1]

            if rising_bit:
                # was previously on local rise. Now checking if slope goes negative.
                if (a[i] - prev_value < 0):
                    # Peak found. Save it. Reset the rising_bit
                    peaks.append(i - 1)
                    rising_bit = 0

            else:
                # Looking for local rise.
                if (a[i] - prev_value) > 0:
                    rising_bit = 1

        return peaks