from __future__ import print_function
import pypruss  # Python PRUSS wrapper
import mmap
from os import path
import struct
import boot         #
import time  # sleep
import BBBIO  # Yields functions for working with GPIO
import settings  # Same function as a .YAML file
import numpy as np
import os

import logging
logging.basicConfig(level=logging.DEBUG, format='%(module)s.py: %(asctime)s - %(levelname)s - %(message)s')

# Global ADC program Constants
PRU0_CR_Mem_Offset = 3
PRU0_THR_Mem_Offset = 4
HC_CR = 0xBEBC200
fclk = 200e6

BIN_DIR = settings.bin_directory

INIT0 = path.join(BIN_DIR, "init0.bin")
INIT1 = path.join(BIN_DIR, "init1.bin")
ADS7865_MasterPRU = path.join(BIN_DIR, "ADS7865_sample.bin")
ADS7865_ClkAndSamplePRU = path.join(BIN_DIR, "pru1.bin")

WORD_SIZE = 12

BYTES_PER_SAMPLE = 4
MIN_SAMPLE_LENGTH = 2
DEFAULT_DAC_VOLTAGE = 2.49612  # volts
DEFAULT_THRESHOLD = 0  # volts
TOTAL_CHANNELS = 4
SAMPLES_PER_CONV = 2

CONV_RATE_LIMIT = 800e3  # Hertz

PLUSMINUS = u'\xb1'.encode('utf-8')
DIFF_PAIR_1 = "CHA0" + PLUSMINUS
DIFF_PAIR_2 = "CHA1" + PLUSMINUS
DIFF_PAIR_3 = "CHB0" + PLUSMINUS
DIFF_PAIR_4 = "CHB1" + PLUSMINUS

CODE_READDAC = 0x103
CODE_SWRESET = 0x105
CODE_READSEQ = 0x106

# Global Functions


def Read_Sample(user_mem, Sample_Length):
    print("ADC: Still have to write documentation about the structure of user_mem variable...")

    with open("/dev/mem", "r+b") as f:  # Open the physical memory device
        ddr_mem = mmap.mmap(f.fileno(), user_mem['filelen'], offset=user_mem['offset'])  # mmap the right area

    y = []
    for i in range(Sample_Length):
        a = user_mem['start'] + i * 4
        b = a + 4
        c = struct.unpack("L", ddr_mem[a:b])[0]  # Parse the data
        y = y + [c, ]
        # print(c)

    return y


def twos_comp(val, bits):
    """compute the 2's compliment of int value val, of n bits."""
    if((val & (1 << (bits - 1))) != 0):
        val = val - (1 << bits)
    return val


def CR_Warn_Programmer():
    logging.warning("Your code updates the conversion rate instead of the"
                    + " sample rate at the end user level. This goes against the"
                    + " design spec, and you should fix it such that your code"
                    + " accepts sample rates at the user level")

###################################
######    ADS7865 Class ###########
###################################

DB_pin_table = ['P9_26', 'P8_46', 'P8_45', 'P8_44', 'P8_43', 'P8_42', 'P8_41', 'P8_40', 'P8_39', 'P8_29', 'P8_28', 'P8_27']
WR_pin = 'P9_31'
BUSY_pin = 'P9_27'
CS_pin = 'P9_25'
RD_pin = 'P9_30'
CONVST_pin = 'P9_29'


class ADS7865:

    """ Allows the user to instantiate an object representing the system
    ADS7865, an analog to digital converter IC by Texas Instruments.
    Incorporates attributes relating to ADC's config, and functions
    for changing the config as well as functions for collecting strings of
    samples in realtime
    """

    def __init__(self, CR=0.0, L=0):
        """ Configures several BBB pins as necessary to hold the ADC in an idle state

        Parameters (in order of initialization):
            self.DBus
            self.WR
            self._RD
            self._CONVST
            self._CS
            self."ddr stuff"
            self.n_channels
            self.convRate
            self.arm_status
            self.seq_desc
            self.ch
            self.threshold
            self.CR_specd
            self.modified
            self.dacVoltage
            self.LSB
        """

        # GPIO Stuff
        self.DBus = BBBIO.Port(DB_pin_table)
        self.DBus.setPortDir("in")

        self.WR = BBBIO.Port(WR_pin)
        self.WR.setPortDir("out")
        self.WR.writeToPort(1)

        self._RD = BBBIO.Port(RD_pin)
        self._RD.setPortDir("out")
        self._RD.writeToPort(1)

        self._CONVST = BBBIO.Port(CONVST_pin)
        self._CONVST.setPortDir("out")
        self._CONVST.writeToPort(1)

        self._CS = BBBIO.Port(CS_pin)
        self._CS.setPortDir("out")
        self._CS.writeToPort(0)

        # PRUSS Stuff
        self.ddr = {}
        self.ddr['addr'] = pypruss.ddr_addr()
        self.ddr['size'] = pypruss.ddr_size()
        self.ddr['start'] = 0x10000000
        self.ddr['filelen'] = self.ddr['size'] + 0x10000000
        self.ddr['offset'] = self.ddr['addr'] - 0x10000000
        self.ddr['end'] = 0x10000000 + self.ddr['size']

        print("ADS7865: Allowing one 32bit memory block per sample, it is "
              + "possible to collect {samp:.1f}K Samples in a single burst. These "
              + "sample points are stored in DDRAM, which is found at the "
              + "address range starting at {addr}".format(
                samp=self.ddr['size'] / 1000.0,
                addr=str(hex(self.ddr['addr'])))
              )

        self.n_channels = 0
        self.convRate = CR
        self.sampleLength = int(L)
        self.arm_status = "unknown"
        self.seq_desc = "unknown"
        self.ch = ['unknown'] * 4
        self.threshold = DEFAULT_THRESHOLD
        self.SR_specd = 0  # parameter for keeping the up with the last spec
        self.modified = True

        # Loads overlays: For that will be later needed for 
        # muxing pins from GPIO to pruout/pruin types and vice versa. 
        boot.load()
        self.SW_Reset()

    ############################
    #### GPIO Commands  #######
    ############################
    def Config(self, cmd_list):
        """ Takes a list of hex values (cmd_list) and bitbangs the ADC
        accordingly. User may refer to the datasheet for an explanation
        of what the hex values actually mean. For examples of correct
        application, see: EZConfig() method
        """

        # Callee save the port direction
        #callee_sPD = self.DBus.portDirection

        #
        for cmd in cmd_list:
            self.WR.writeToPort(0)  # Open ADC's input Latch

            self.DBus.setPortDir("out")  # Latch open, safe to make DB pins an out
            self.DBus.writeToPort(cmd)  # Write the value to the DB pins

            print('ADS7865: Databus cmd %s has been sent.' % self.DBus.readStr())
            self.WR.writeToPort(1)  # Latch down the input

        self.DBus.setPortDir("in")  # Return DB pins back to inputs.

    def EZConfig(self, sel=None):
        """ Allows the user to access commonly used config command (presets).

        Args:
            sel: An integer from 0 to 5 representing a particular preset
        """

        # NOTES TO USER
        #--At powerup, sequencer_register=0x000
        #--Capturing one channel (non-pair) in isolation is doable by selecting sel=0
        # or sel=1 (since ADS7865 resets the data_output pointer at the beginning of every
        # CONVST), but the user must also take the extra precaution to disable the
        #"sub-sampling" portion of the PRUSS code in order for it to work.

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

        ## ##
        # Single channel (pair) enable
        if sel == 0:
            # User has chosen to sample the 0a/0b differential channel pair.
            self.Config([0x100])

            # Update statuses
            seq = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, '', '']
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 2

        elif sel == 1:
            # User has chosen to sample the 1a/1b differential channel pair.
            self.Config([0xD00])

            # Update statuses
            seq = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, '', '']
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 2

        ## ##
        # Single channel (pair) enable with sequencer reinitialization
        elif sel == 2:
            # User has chosen to sample the 0a/0b differential channel pair
            # while disabling the sequencer register. NOTE: The reason why
            # this would ever be necessary is unclear, as it seems to have
            # the same functionality of EZConfig 0.
            self.Config([0x104, 0x000])

            # Update statuses
            seq = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, '', '']
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 2

        elif sel == 3:
            # User has chosen to sample the 1a/1b differential channel pair
            # while disabling the sequencer register NOTE: The reason why
            # this would ever be necessary is unclear, as it seems to have
            # the same functionality of EZConfig 1.
            self.Config([0x304, 0x000])

            # Update statuses
            seq = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, '', '']
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 2

        ## ##
        # Dual channel (pair) enable
        elif sel == 4:
            # User has chosen to sample the 0a/0b -> 1a/1b in FIFO style
            self.Config([0x104, 0x230])

            # Update statuses
            seq1 = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            seq2 = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
            seq = seq1 + " -> " + seq2
            chans = [DIFF_PAIR_1, DIFF_PAIR_3, DIFF_PAIR_2, DIFF_PAIR_4]
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 4

        elif sel == 5:
            # User has chosen to sample the 1a/1b -> 0a/0b in FIFO style
            self.Config([0x104, 0x2c0])

            # Update statuses
            seq1 = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            seq2 = "CHA1" + PLUSMINUS + "/CHB1" + PLUSMINUS
            seq = seq1 + " -> " + seq2
            chans = [DIFF_PAIR_2, DIFF_PAIR_4, DIFF_PAIR_1, DIFF_PAIR_3]
            self.Update_Config_Text(seq, chans)

            # Update n channels
            self.n_channels = 4

        if self.SR_specd:       # Last parameter that the user specd was SR
            self.Update_SR(self.sampleRate)
        else:
            CR_Warn_Programmer()

    def Preset(self, sel):
        if sel==0:
            self.Set_SL(1e3)
            self.Update_SR(400e3)
            self.threshold = 0
            self.EZConfig(4)
            
        elif sel==1:
            self.Set_SL(1e3)
            self.Update_SR(800e3)
            self.threshold = 0
            self.EZConfig(0)
            
        else:
            logging.warning("Unknown preset!")
            
    def Read_Seq(self):
        # Send cmd telling ADC to output it's SEQ config
        self.Config([CODE_READSEQ])

        # Read ADC's databus
        self._RD.writeToPort(0)
        seq = self.DBus.readStr()
        self._RD.writeToPort(1)

        # print config to the user
        print("Config of sequencer: %s" % seq)

    def Read_Dac(self):
        # Send cmd telling ADC to output it's SEQ config
        self.Config([CODE_READDAC])

        # Read ADC's databus
        self._RD.writeToPort(0)
        dac_s = self.DBus.readStr()
        self._RD.writeToPort(1)

        # print config to the user
        print("Config of DAC: %s" % dac_s)

        # interpret value
        dac_voltage_readout = self.Conv_Dac_Str_to_Voltage(dac_s)
        print("... Vdac = %.5f volts" % dac_voltage_readout)

        # Update DAC related atributes
        self.dacVoltage = dac_voltage_readout
        self.LSB = self.dacVoltage / (2**(WORD_SIZE - 1))  # Volts

    def Update_CR(self, CR):
        # Update modified bit
        self.modified = True
        
        # Update Conversioning bit
        self.convRate = float(CR)
        self.sampleRate = self.CR_2_SR(CR)

        if (CR > CONV_RATE_LIMIT):
            logging.warning("Your spec'd conversion rate"
                            + " exceeds the system's spec (%dKHz)" % CONV_RATE_LIMIT / 1000)

        self.SR_specd = 0

    def Update_SR(self, SR):
        # Update modified bit
        self.modified = True
        
        # Update sampling bits
        self.sampleRate = float(SR)
        self.convRate = self.SR_2_CR(SR)

        self.SR_specd = 1

        if (self.convRate > CONV_RATE_LIMIT):
            logging.warning("Your spec'd conversion rate"
                            + " exceeds the system's spec (%dKHz)" % CONV_RATE_LIMIT / 1000)
    
    def Set_SL(self,SL):
        self.sampleLength = int(SL)
        

    def SW_Reset(self):
        print("Performing ADC device reset...")
        self.Config([CODE_SWRESET])

        # DAC outputs the default voltage
        self.dacVoltage = DEFAULT_DAC_VOLTAGE
        self.LSB = self.dacVoltage / (2**(WORD_SIZE - 1))  # Volts

        # Update sequencer and channel descriptions
        self.seq_desc = "CHA0" + PLUSMINUS + "/CHB0" + PLUSMINUS
        self.ch[0] = DIFF_PAIR_1
        self.ch[1] = DIFF_PAIR_3
        self.ch[2] = ''
        self.ch[3] = ''

        # Update other parameters
        self.n_channels = 2
        self.Update_CR(self.convRate)
        self.modified = True

        # Let user know work is done
        print("... done.")

    def Close(self):
        self._CS.writeToPort(1)
        self.DBus.close()
        self.WR.close()
        self._RD.close()
        # do not close# self.BUSY.close()
        self._CS.close()
        self._CONVST.close()

    ############################
    # General ADC Commands  #####
    ############################
    def Update_Config_Text(self, seq, channels):
        # Update human readable description
        self.seq_desc = seq

        # Update channel descriptions
        for i in range(TOTAL_CHANNELS):
            self.ch[i] = channels[i]

    def V_to_12bit_Hex(self, Vin):
        return int(round(Vin / self.LSB))

    def Conv_Dac_Str_to_Voltage(self, dac_s):
        """ Interprets the data 12 bit binary output of an ADC DAC read cmd,
        represented by the string dac_s
        """

        # DAC value Conversion Constant
        V_per_bit = 0.00244  # Volts/bit
        base_2 = 2

        dac_i = int(dac_s, base_2)
        dac_v = dac_i * V_per_bit

        return dac_v

    def CR_2_SR(self, CR):
        if (self.n_channels != 0):
            return (CR * SAMPLES_PER_CONV) / float(self.n_channels)
        else:
            logging.warning("self.n_channels == 0. Unable to compute self.sampleRate!")
            return None

    def SR_2_CR(self, SR):
        if (self.n_channels != 0):
            return (SR) * (self.n_channels / float(SAMPLES_PER_CONV))
        else:
            logging.warning("self.n_channels == 0. Unable to compute self.sampleRate!")
            return None

    def ADC_Status(self):
        # Read and write pins
        _RD = eval(self._RD.readStr())
        _WR = eval(self._RD.readStr())
        print("  _RD:\t%d" % _RD)
        print("  _WR:\t%d" % _WR)

        # Conversion and sample rate
        cr = self.convRate
        print("  cr:\t%.2e conversions/sec" % cr)
        print("  sr:\t%.2e samples/sec" % self.sampleRate)

        # Sample length
        sl = self.sampleLength
        print("  sl:\t%d samples" % sl)

        # Threshold
        print("  thr:\t%d Volts" % self.threshold)

        # arm status
        armed = self.arm_status
        print("  armed:\t%s" % armed)

        # channel config
        print("  config:\t{}".format(self.seq_desc))

        # get channels
        for i in range(4):
            print("  channel {}:\t{}".format(i, self.ch[i]))

    def Generate_Matching_Time_Array(self, M):
        """ For plotting signals in the time domain.

        Looks at it's sampling parameters, and generate a numpy array
        of length M to corresponds with M samples of data per channel
        """
        Ts = 1 / self.sampleRate

        if (M * Ts / Ts <= M):
            t = np.arange(0, M * Ts, Ts)

        elif (M * Ts / Ts > M):
            t = np.arange(0, (M - 0.1) * Ts, Ts)  # Chalk it up to precision error

        else:
            print("Something crazy happened.")
            t = None

        return t

    ############################
    #### PRUSS Commands  #######
    ############################
    def Ready_PRUSS_For_Burst(self, CR=None):
        """Arms the ADC for sample collection. This removes some GPIO control
        from the BBB, and replaces it with PRUIN/OUT control.
        """
        
        # Initialize variables
        if CR is None:
            CR = self.convRate
        else:
            self.convRate = CR

        if CR == 0:
            print("CR currently set to 0. Please specify a conversion rate.")
            exit(1)

        CR_BITECODE = int(round(1.0 / CR * fclk))  # Converts user CR input to Hex.

        # Initialize evironment
        pypruss.modprobe()
        pypruss.init()      # Init the PRU
        pypruss.open(0)     # Open PRU event 0 which is PRU0_ARM_INTERRUPT
        pypruss.pruintc_init()  # Init the interrupt controller

        # INIT PRU Registers
        pypruss.exec_program(0, INIT0)  # Cleaning the registers
        pypruss.exec_program(1, INIT1)  # Cleaning the registers
        pypruss.pru_write_memory(0, 0x0000, [0x0, ] * 0x0800)  # clearing pru0 ram
        pypruss.pru_write_memory(0, 0x0800, [0x0, ] * 0x0800)  # clearing pru1 ram
        pypruss.pru_write_memory(0, 0x4000, [0x0, ] * 300)  # clearing ack bit from pru1
        pypruss.pru_write_memory(0, PRU0_CR_Mem_Offset, [CR_BITECODE, ])  # Setting conversion

        pypruss.exec_program(1, ADS7865_ClkAndSamplePRU)        # Load firmware on PRU1

        # end readying process by arming the PRUs
        boot.arm()
        self.arm_status = 'armed'
        self.modified =False
    
    def Unready(self):
        """Gives GPIO control back to the the beaglebone.
        """
        
        if (self.arm_status == 'unarmed'):
            logging.warning("ADC Already dearmed!!! You are double dearming somewhere.")
        else:
            print('ADS7865: Dearming the PRUSS')
            boot.dearm()
            self.arm_status = 'unarmed'

    def Reload(self):
        """ Re-initializes the PRU's interrupt that this library uses to tell
        python that it can continue running code again. This must be called at
        the end of a function that utilizes this interrupt. The calling
        function should not be responsible for reloading PRUs
        """
        pypruss.init()      # Init the PRU
        pypruss.open(0)     # Open PRU event 0 which is PRU0_ARM_INTERRUPT
        pypruss.pruintc_init()  # Init the interrupt controller

    def Burst(self, length=None, n_channels=None, raw=None, fmt_volts=1):
        """
        Args:
            length:
            n_channels:
            raw:
            fmt_volts:
        """
        if length is None:  # Optional argument for sample length
            length = self.sampleLength
        else:
            self.sampleLength = int(length)

        if n_channels is None:
            n_channels = self.n_channels
        else:
            self.n_channels = n_channels

        # Share DDR RAM Addr with PRU0
        pypruss.pru_write_memory(0, 1, [self.ddr['addr'], ])

        # Share SL with PRU0: pru_SL_mapping just incorporates
        # some math that translates the user specified SL parameter
        # to a byte addressible memory size value that the PRU will use to
        # check whether it has finished writing it's data to the
        # memory
        pru_SL_mapping = (length - MIN_SAMPLE_LENGTH) * BYTES_PER_SAMPLE
        pypruss.pru_write_memory(0, 2, [pru_SL_mapping, ])

        # Share Threshold with PRU0
        thr_hex = self.V_to_12bit_Hex(self.threshold)
        pypruss.pru_write_memory(0, PRU0_THR_Mem_Offset, [thr_hex, ])

        # Launch the Sample collection program
        a = time.time()
        pypruss.exec_program(0, ADS7865_MasterPRU)  # Load firmware on PRU0

        # Wait for PRU to finish its job.
        pypruss.wait_for_event(0)  # Wait for event 0 which is conn to PRU0_ARM_INTERUPT
        b = time.time()
        t = b - a

        # Once signal has been received, clean up house
        # pypruss.clear_event(0) # Clear the event
        # pypruss.exit()         # Exit PRU

        # Read the memory
        raw_data = Read_Sample(self.ddr, length)

        y = [0] * n_channels
        for chan in range(n_channels):

            # user may specify whether he wants a numpy array
            # ... or not.
            y[chan] = np.asarray(raw_data[chan::n_channels])

            # User may specify whether he wants values to come in
            # raw, or two's compliment.
            if (raw is None) or (raw == 0):
                i = 0
                for samp in y[chan]:
                    y[chan][i] = twos_comp(samp, WORD_SIZE)
                    i += 1

                # Assuming that the user is requesting 2 compliment values,
                # it is possible to do conversion to voltage values. How ever,
                # if the user has set raw to True, then this option is
                # unavailable.
                if fmt_volts:
                    y[chan] = y[chan] * self.LSB

        self.Reload()

        return y, t
        
    def GetData(self):
        if not (self.arm_status=='armed' and self.modified==False):
            self.Ready_PRUSS_For_Burst()
        
        y, t = self.Burst()
        return y
        
       
