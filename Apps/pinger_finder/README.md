# Pinger Finder
An application that computes position vectors pointing to the hydrophone location, and relays that information back to seawolf.

# How to run it
**Step 1: Building the executable files**
Simply issue the following command

     make
 
**Step 2: Run the program**
Issue the following command to run the program

     python main.py n

whereas n is the number of samples that the ADC will collect and return to the user. Some diagnostic information will be displayed in order to indicate how quickly these samples were captured. To review the data collected, print out the "y" variable from main.py.

# Cleaning up.
If things get messy, just run

     make clean

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


