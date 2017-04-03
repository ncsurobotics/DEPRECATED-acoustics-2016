
### dependencies / configs
This code depends on some external libraries, namely SciPy and PyPRUSS. To run this code, your must have/do the following:

  * **python2.7**
  * **SciPy**: Mostly for human interface stuff where plotting is involved.
  * **Disable the HDMI Cape on the BBB**: This will free up some many of the PRUSS-ICSS pins.
  * **pypruss**: a python wrapper for the c library responsible for sending high level commands to the PRUSS-ICSS.
  * **pasm**: Compiler for the PRU assembly code. Seems to be included with beaglebones manufactured after April.
  * **beaglebone-universal-io**: Collection of scripts that allow user to assign PRUSS.
  * **Make a cron job for terminal app**: This allows seawolf to interact with acoustics without ssh.

To take care of these dependencies, please follow the steps below.

**(Optional) Make an Installs directory.**  
You don't have to do this, but it might be nice to have. The installs directory will act as a point of reference in this short guide.

     mkdir ~/Installs/
     cd Installs/
     
**Install SciPy**  
Installing scipy is easiest if you follow the official instruction on this webpage:

    https://www.scipy.org/install.html

*NOTE WELL*: When you purform this install, it is very likely that matplotlib won't install properly due to numpy being some old version (version 1.6.x in the most recent case). matplotlib requires version newer than 1.7.x. To update numpy, simply run this command:

     pip install --upgrade numpy
     
**Install steinkuehler's BBB universal device tree scripts**  

     git clone https://github.com/cdsteinkuehler/beaglebone-universal-io.git
     cd /beaglebone-universal-io/
     make 
     make install
 
Now you can issue the command "config-pin" from the commandline and use it for easily manipulate some of the IO/Muxes. The boot.py script takes advantage of this. Also, the makefile had several .dtbo files get copied to the firmware directory as well.
 
**Disable the HDMI control**  
We used to use this adafruit tutorial (https://learn.adafruit.com/setting-up-wifi-with-beaglebone-black/hardware) to disable the HDMI output from the BBB. The relevant part of it is the section labeled "HDMI Port Interference", where it talks about manipulating the uEnv.txt file. The instructions were used to disable the HDMI cape on the BBB (Which frees up a lot of important pins for controlling the ADC). 
**Unfortunately, BBB's software has changed since that tutorial was written, so the steps are no longer the same.** The steps below were used on a new BBB in April of 2017, but you should keep in mind that the process may have changed since this guide was last updated.

For reference, here's what was done on the lab BBB:

	**Step One**
```
mkdir /mnt/boot
mount /dev/mmcblk0p1 /mnt/boot/
```
The problem is that "uEnv.txt", which you need to edit, is no longer located here. I am not sure if this step was necessary, but I wanted to document that we did it. After lots of searching on the internet, we figured out that uEnv.txt is now located in /boot/, so you simply edit it from a new location. Once you open the file, uncomment the line under the heading "##Disable HDMI (v3.8.x). Save the file, reboot the BBB and keep going.

**Do not uncomment a line under a heading similar to "Beaglebone Black: HDMI (Audio/Video) disabled:** If you do so all four of the user LED's will turn on and you will not be able to ssh in. If that happens, however, don't panic: you may still be able to plug the BBB into your computer and access it as a USB device (use Linux for this). You can then edit the uEnv.txt file from your computer and comment out the line again.
The same goes for any line that talks about disabling eMMC. eMMC is the beaglebone's main onboard memory so that would be... less than advisable.

**Install Pypruss from source**  
Go to the Pypruss Bitbucket repository(https://bitbucket.org/intelligentagent/pypruss) and follow their instructions. Pypruss was installed on the lab beaglebone by...

     cd ~/Installs/
     git clone https://bitbucket.org/intelligentagent/pypruss.git  
     cd pypruss
     python setup.py install
     vim ~/.bashrc #Append "export LD_LIBRARY_PATH=/usr/local/lib" to end of file
     source ~/.bashrc

**Make a cron job for acoustics terminal**  
Doing this will get the BBB to run `acoustics_terminal.py` at startup. With the FT232RL connected and every thing, getting seawolf to communicate with acoustics is only a matter of sending commands out of seawolf's USB port. There will be no ssh/login overhead. To get this to work, simply type

    crontab -e
    ## to end of file, replacing <path_to_proj_dir> with the path to 
    ## this very directory 
    sudo reboot #For the changes to take effect

then append then append the following to the end of the text file.

@reboot python <path_to_proj_dir>/host_communication/test/acoustics_echoterm &

Replacing <path_to_proj_dir> with the path to this very directory

After all this, you are totally ready to run the the `pinger_finder` software. Instructions for how to do this are at the top.

