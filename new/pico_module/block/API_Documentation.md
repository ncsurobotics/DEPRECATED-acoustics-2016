# Table of Contents
- [Building](#building)
- [Python](#python)
- [Changing Settings](#changing-settings)
  - [Notes](#notes)
  - [`#define` constants](#define-constants)
    - [Frequently modified](#frequently-modified)
    - [Rarely Modified](#rarely-modified)
    - [Deprecated (block)](#deprecated-block)
    - [Non-verified](#non-verified)
  - [`g_*` variables](#g_-variables)
    - [Rarely modified](#rarely-modified-1)
- [Functions](#functions)
  - [`pico_config()`](#pico_config)
    - [Description](#description)
    - [Parameters](#parameters)
    - [Returns](#returns)
  - [`pico_init()`](#pico_init)
    - [Description](#description-1)
    - [Parameters](#parameters-1)
    - [Returns](#returns-1)
  - [`pico_get_data()`](#pico_get_data)
    - [Description](#description-2)
    - [Parameters](#parameters-2)
    - [Returns](#returns-2)
  - [`pico_close()`](#pico_close)
    - [Description](#description-3)
    - [Parameters](#parameters-3)
    - [Returns](#returns-3)
  - [`pico_get_sample_interval()`](#pico_get_sample_interval)
    - [Description](#description-4)
    - [Parameters](#parameters-4)
    - [Returns](#returns-4)
  
# Building
Assuming the picoscope driver libraries are properly installed, `sh build.sh` will build the block_module.

TODO: Convert to makefile.

# Python
View the `sample.py` file for an example work flow. Module is improted with `import pico_module`.

# Changing Settings
## Notes
Currently, settings must be changed by modifying the `#define` constants at the top of the block_module.c file and a few global `g_*` variables. Whenever the settings are changed, the file must be rebuilt. Future versions should move away from having `#define` constants used as configuration values and instead be used as default values. Configuration values should be moved either to global `g_*` variables or the `CONFIG` `struct` and handled by the `pico_config()` function.

Perhaps ideally in the future all configuration variables should be moved to the `CONFIG` `struct` and set by `pico_config()`.

All variables not listed here should not be modified, or modifying them has no effect on the program (IE they are set by the program).

## `#define` constants
### Frequently modified
* `THRESHOLD` - The threshold value for a trigger to occur. Has a range of `-32512` (-100%) to `32512` (100%). `INPUT_VOLTAGE` (below) provides context for what those values mean. Example: for PS2000A_100MV -- `THRESHOLD` = `16512` means the trigger will occur at 50%, or 50mv.
* `INPUT_VOLTAGE` - This is the voltage range for the output data. It uses named constants from `libps2000a-1.1/ps2000aApi.h`. See the table below for valid values. Note that the actual output by the driver is always the same (`-32512` to `32512`), but this setting gives it meaning (Example: for `PS2000A_100MV` -- 100mv = `32512`, -50mv = `-16256` ). The value in **bold** has been found to work in most situations for the hardware at the time of this writing (2018-06-06)

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
* `DEF_DIRECTION` - The signal direction for a trigger to occur. Uses named constants from `libps2000a-1.1/ps2000aApi.h`. See table below for values. **Bolded** value is the one we use. See the [PS2000A API](https://www.picotech.com/download/manuals/ps2000apg.en-6.pdf) for more details on what each constant means.

Constant Value  
--------------
**PS2000A_RISING**
PS2000A_RISING_LOWER
PS2000A_FALLING
PS2000A_FALLING_LOWER
PS2000A_RISING_OR_FALLING

### Deprecated (block)
* `TIME_UNITS` - Not used for block mode

### Non-verified
* `PRE_TRIGGER_SAMPLES` - **It has not yet been confirmed if this has any effect on the operation of the program.** It is supposed to set the number of samples recorded and returned before a trigger occures.
* `AUTO_TRIG_MS` - **It has not yet been confirmed if this has any effect on the operation of the program.** It is supposed to automatically trigger data collection after X milliseconds have passed with no trigger (so the picoscope doesn't get 'stuck').

## `g_*` variables
### Rarely modified
* `g_timebase` - This value 'seeds' the program with a target timebase. The picoscope driver then finds a supported timebase for the unit. Valid values are `0` to `2^32 - 1`. A lower value gives higher sampling rate. See the [PS2000A API](https://www.picotech.com/download/manuals/ps2000apg.en-6.pdf) for more details on how timebase is calculated.

# Functions
## `pico_config()`
### Description
#### `pico_config(/* TODO */)`
In the future, this method will be able to be called with all the available configuration options so the module will not need to be rebuilt each time.
### Parameters
`/* TODO */`
### Returns
`/* TODO */`
## `pico_init()`
#### `pico_init(int debug)`
### Description
Must be called before `pico_get_data()` and `pico_close()`. Connects to and initializes the picoscope. Initialization includes allocating memory, configuring channels, and establishing the timebase (sampling rate).
### Parameters
Parameter | Description
--------------|-------------
int debug | 0 = false. When enabled, outputs some debugging/logging information to the terminal window.
### Returns
Returns the handle for the picoscope. **This must be saved in your python code in order to retrieve data and properly close the unit.**
## `pico_get_data()`
#### `pico_get_data(int handle)`
### Description
Retrieves the next data sample available (whenever the next trigger occures). Can be called repeatedly between opening and closing the unit. Must call `pico_get_sample_interval()` to determine the sampling interval of the data (otherwise the data has no real meaning).
### Parameters
Parameter | Description
--------------|-------------
int handle | The handle value returned by `pico_init()`.
### Returns
Returns a 2D array containing the captured values. The array has the format `arr[CHANNEL][SAMPLE]`. 
## `pico_close()`
#### pico_close(int handle)
### Description
Closes the picoscope. Must be called before the python program closes or else the resources will be list and the device must be unplugged.
### Parameters
Parameter | Description
--------------|-------------
int handle | The handle value returned by `pico_init()`.
### Returns
Nothing.
## `pico_get_sample_interval()`
#### pico_get_sample_interval()
### Description
Returns the actual sampling interval used by the picoscope.
### Parameters
None.
### Returns
Returns the actual sampling interval used by the picoscope.
