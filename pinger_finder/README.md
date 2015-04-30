# Pinger Finder
An application that computes position vectors pointing to the hydrophone location, and relays that information back to seawolf.


# Running the debugger program
**Step 0: Building the executable files and installing dependencies**  
Instructions for taking care of all the dependancies are given in the section labeled "Dependencies" below. The lab Beaglebone should have all this taken care of, so generally it's safe to move on to the next step if you're using the lab Beaglebone.

**Step 0.1: Run make to compile any changes in the source code if necessary**  
Simply issue the following command

     make
 
 This will compile the assembly code that the PRUs use, and stick the object files in the bin directory.
 
**Step 1: Run the program**

Issue the following command to run the program

     python main.py      # << type "help" in immediate prompt for more instructions.
                         # BUG: "(l)oad_ADC" Usually doesn't work on first time after fresh boot. 
                         # type "(u)nload_ADC" and then "(l)oad_ADC" if a message of zero memory
                         # allocation shows up.

# Cleaning up
If things get messy, just run

     make clean

# Dependencies / Configs
See similarly name section of the README in the projects root directory.


# Pin i/o allocation 
**(Needs to be updated. Consult <ElectricalDropbox>/2014/Acoustics/Schematics/Pinger Sensor/BBB Pinout.svg for a more up to date diagram).**

## I/0
DB0:  P8.27

DB1:  P8.28

DB2:  P8.29

DB3:  P8.39

DB4:  P8.40

DB5:  P8.41

DB6:  P8.42

DB7:  P8.43

DB8:  P8.44

DB9:  P8.45

DB10: P8.46

DB11: P9.31 ()

## Inputs
BUSY: 


## Outputs
WR:
CONVST:

# Troubleshooting
**Segmentation faults**  
getting...

    ...
    AM33XX
    File bin/init0.bin open failed
    Segmentation fault


...means that the .bin files haven't been compiled yet (.bins hold the binary that is loaded on the PRUs). Simply issue a "Make" command from the commandline to generate the .bin files.

