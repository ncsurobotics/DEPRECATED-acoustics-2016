# acoustics
Acoustics code for ncsurobotics' 2015 robot, Seawolf VI

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
Install SciPy using your package manager, eg.

    sudo apt-get install python-scipy
     
**Install steinkuehler's BBB universal device tree scripts**  

     git clone https://github.com/cdsteinkuehler/beaglebone-universal-io.git
     cd /beaglebone-universal-io/
     make 
     make install
 
Now you can issue the command "config-pin" from the commandline and use it for easily manipulate some of the IO/Muxes. The boot.py script takes advantage of this. Also, the makefile had several .dtbo files get copied to the firmware directory as well.
 
**Disable the HDMI control**  
Go to this adafruit tutorial (https://learn.adafruit.com/setting-up-wifi-with-beaglebone-black/hardware), find the section labeled "HDMI Port Interference", and go to the part about manipulating the uEnv.txt file. These instructions are how to disable the HDMI cape on the BBB (Which will free up a lot of important pins for controlling the ADC). Follow them. For reference, here's what was done on the lab BBB:

     mkdir /mnt/boot
     mount /dev/mmcblk0p1 /mnt/boot/
     nano /mnt/boot/uEnv.txt            #Uncomment the correct line... as said in the tutorial.
     sudo reboot                        #You will have to ssh back in to the BBB after this.
 
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

