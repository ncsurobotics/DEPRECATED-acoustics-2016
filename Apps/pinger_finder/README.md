# Pinger Finder
An application that computes position vectors pointing to the hydrophone location, and relays that information back to seawolf.

# Dependencies
To run this program, you must have/do the following:

  * **python2.7**
  * **Disable the HDMI Cape on the BBB**: This will free up some many of the PRUSS-ICSS pins.
  * **pypruss**: a python wrapper for the c library responsible for sending high level commands to the PRUSS-ICSS.
  * **pasm**: Compiler for the PRU assembly code. Seems to be included with beaglebones manufactured after April.
  * **beaglebone-universal-io**: Collection of scripts that allow user to assign PRUSS.

To take care of these dependencies, please follow the steps below.

**Step 0: Make an Installs directory.**

You don't have to do this, but it might be nice to have. The installs directory will act as a point of reference in this short guide.

     mkdir ~/Installs/
     cd Installs/
     
**Step 1: Install steinkuehler's BBB universal device tree scripts**

     git clone https://github.com/cdsteinkuehler/beaglebone-universal-io.git
     cd /beaglebone-universal-io/
     make 
     make install
     
Now you can issue the command "config-pin" from the commandline and use it for easily manipulate some of the IO/Muxes. The boot.py script takes advantage of this. Also, the makefile had several .dtbo files get copied to the firmware directory as well.
 
**Step 2: Disable the HDMI control**

Go to this adafruit tutorial (https://learn.adafruit.com/setting-up-wifi-with-beaglebone-black/hardware), find the section labeled "HDMI Port Interference", and go to the part about manipulating the uEnv.txt file. These instructions are how to disable the HDMI cape on the BBB (Which will free up a lot of important pins for controlling the ADC). Follow them. For reference, here's what was done on the lab BBB:

     mkdir /mnt/boot
     mount /dev/mmcblk0p1 /mnt/boot/
     nano /mnt/boot/uEnv.txt            #Uncomment the correct line... as said in the tutorial.
     sudo reboot                        #You will have to ssh back in to the BBB after this.
 
**Step 3: install Pypruss from source**
Go to the Pypruss Bitbucket repository(https://bitbucket.org/intelligentagent/pypruss) and follow their instructions. Pypruss was installed on the lab beaglebone by...

     cd ~/Installs/
     git clone https://bitbucket.org/intelligentagent/pypruss.git  
     cd pypruss
     python setup.py install
     vim ~/.bashrc #Append "export LD_LIBRARY_PATH=/usr/local/lib" to end of file
     source ~/.bashrc

After this, you are totally ready to run the this pinger_finder software. Go on to the next section for instructions how.

# How to run it
**Step 1: Building the executable files**

Simply issue the following command

     make
 
**Step 2: Run the program**

Issue the following command to run the program

     python main.py n    #BUG: Usually doesn't work on first time after boot. 
                         #^^Try again if some error regarding the mmc shows up.

whereas n is the number of samples that the ADC will collect and return to the user. Some diagnostic information will be displayed in order to indicate how quickly these samples were captured. To review the data collected, print out the "y" variable from main.py.

# Cleaning up
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


