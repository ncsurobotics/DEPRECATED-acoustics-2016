# Host Communication App

This is meant to be the program that seawolf will run in order to 
send and recieve commands/data to/from the beaglebone.

This is a WIP. Below is a list of features that need to be implemented in
in order to complete this project:

[ ] Remotely run any program found on the beaglebone using this app.

[ ] Remotely request and recieve data from the beaglebone using this app.

## How to run the program

cd into this project directory if you haven't already

    root@beaglebone:~/Projects/acoustics# cd <proj-dir>/acoustics/Apps/Host_Communication_App/

Make sure the [FT232RL Breakout board](https://www.sparkfun.com/products/12731)
 is connected to the host computer. Also, make sure the board's breakout pins
are connected such that the beaglebone can at least transmit UART messages
 to the breakout board. then simply run `python main.py` from
 the terminal screen to run the program.

As of the current state of this program. A screen will appear to say
"listening" which means you can transmit UART messages from the
beaglebone and see see them displayed on the host's terminal screen. 
If you would like test this, simply open another terminal screen to
act like the client beaglebone, and follow the steps from the "how
to write UART from the beaglebone" section below. 

## How to write UART from the beaglebone:

Manually:

The manual method involves running this list of commands:

    root@beaglebone:~# config-pin -a P9.13 uart

This will enable the uart tx on  pin 13 header 9. (If you're ever unsure
what a pin does, you have access to the `config-pin -q <pin>` or 
`config-pin -i <pin>` commands, as well as the master UART table that 
can be soon found in the wiki of this github)

Now, sending commands is a matter of "echoing" text into the correct 
file representing the UART system:

    root@beaglebone:~# echo --insert message here-- > /dev/ttyO4

# Troubleshooting
**Don't know port to initialize for pyserial**  
Run this command in the terminal to show a list of possible serial ports

    python -m serial.tools.list_ports

On the beaglebone, this command will take ~30 seconds to complete, but it should show a concise list of all the available serial ports on the beaglebone.

**BBB not reading uart input data**  
Possible that backend terminal processing is missing something that will tell it to "print <x> to screen". To check, enter

    stty -F /dev/ttyO<uart_port#> -a

to check on the port's settings, or enter

    stty -F /dev/ttyO<uart_port#> raw

To see circumvent terminal processing and verify that signals are reaching the target RX pin at all.
