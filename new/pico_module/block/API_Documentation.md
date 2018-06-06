# Table of Contents
- [Changing Settings](#changing-settings)
  - [Details](#details)
  

# Changing Settings
### Details
Currently, settings must be changed by modifying the `#define` constants at the top of the block_module.c file and a few `g_*` variables. Whenever the settings are changed, the file must be rebuilt.

## `#define` constants
### Frequently modified
* `THRESHOLD` - 
* `INPUT_VOLTAGE` - This is the voltage range for the output data. It uses named constants from `libps2000a-1.1/ps2000aApi.h`. See the table below for valid values. Note that the actual output by the driver is always the same (`-32512` to 32512`), but this setting gives it meaning (Example: for `PS2000A_100MV` -- 100mv = `32512`, -50mv = `-16256` ). The value in **bold** has been found to work in most situations for the hardware at the time of this writing (2018-06-06)

Millivolts    | Volts
--------------|-------------
PS2000A_20MV  | PS2000A_1V
PS2000A_50MV  | PS2000A_2V
**PS2000A_100MV** | PS2000A_5V
PS2000A_200MV | PS2000A_10V
PS2000A_500MV | PS2000A_20V

### Rarely modified
* `NUM_SAMPLES` - In block mode, this has a soft upper limit of 48000 / number of active channels = **12000**
* `NUM_CHANNELS` - The number of channels that the oscilloscope reads data from
* `DEF_SAMPLE_INTERVAL` - Manually setting this in block mode has no effect. 
* `DEF_DIRECTION`

### Deprecated (block)
* `TIME_UNITS` - Not used for block mode
* `PRE_TRIGGER_SAMPLES`


# Methods
## pico_config()
### Details
In the future, this method can be called 
## pico_init()
## pico_get_data()
## pico_close()
## pico_get_sample_interval()
