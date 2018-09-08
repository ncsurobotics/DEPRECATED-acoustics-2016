# Table of Contents
- [Building](#building)
- [Python](#python)
- [Default Values and Constants (block_module.c)](#default-values-and-constants-block_modulec)
  - [Notes](#notes)
  - [`#define` constants](#define-constants)
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
View the `sample.py` file for an example work flow. Module is imported with `import pico_module`.

# Default Values and Constants (block_module.c)
## Notes
All variables not listed here should not be modified, or modifying them has no effect on the program (IE they are set by the program).

## `#define` constants
The `#define`'d constants specify default settings and should only be changed if the sub hardware changes. Otherwise, `pico_config` should be used.

* `DEF_NUM_CHANNELS` - The number of channels that the oscilloscope reads data from. Generally = **4**.
* `DEF_DIRECTION` - The signal direction for a trigger to occur. Uses named constants from `libps2000a-1.1/ps2000aApi.h`. See table below for values. **Bolded** value is the one we use. See the [PS2000A API](https://www.picotech.com/download/manuals/ps2000apg.en-6.pdf) for more details on what each constant means.

Option |
-------|
**PS2000A_RISING** |
PS2000A_FALLING |
PS2000A_ABOVE |
PS2000A_BELOW |
PS2000A_RISING_OR_FALLING |

* `DEF_THRESHOLD` - The threshold value for a trigger to occur. Has a range of `-32512` (-100%) to `32512` (100%). `INPUT_VOLTAGE` (below) provides context for what those values mean. Example: for PS2000A_100MV -- `THRESHOLD` = `16512` means the trigger will occur at 50%, or 50mv. Default value is **6000**
* `DEF_NUM_SAMPLES` - In block mode, this has a hard upper limit of 48000 / number of active channels = **12000**
* `DEF_INPUT_VOLTAGE` - This is the voltage range for the output data. It uses named constants from `libps2000a-1.1/ps2000aApi.h`. See the table below for valid values. Note that the actual output by the driver is always the same (`-32512` to `32512`), but this setting gives it meaning (Example: for `PS2000A_100MV` -- 100mv = `32512`, -50mv = `-16256` ). The value in **bold** has been found to work in most situations for the hardware at the time of this writing (2018-06-06)

Millivolts    | Volts
--------------|-------------
PS2000A_20MV  | PS2000A_1V
PS2000A_50MV  | PS2000A_2V
**PS2000A_100MV** | PS2000A_5V
PS2000A_200MV | PS2000A_10V
PS2000A_500MV | PS2000A_20V

* `DEF_SAMPLE_INTERVAL` - Manually setting this in block mode has no effect. 
* `DEF_PRE_TRIGGER_SAMPLES` - **It has not yet been confirmed if this has any effect on the operation of the program.** It is supposed to set the number of samples recorded and returned before a trigger occures.
* `DEF_AUTO_TRIG_MS` - **It has not yet been confirmed if this has any effect on the operation of the program.** It is supposed to automatically trigger data collection after X milliseconds have passed with no trigger (so the picoscope doesn't get 'stuck').
* `DEF_TIMEBASE` - The starting value for searching for a timebase. Default value is **35**. See the [PS2000A API](https://www.picotech.com/download/manuals/ps2000apg.en-6.pdf) for more information on timebases.

# Functions
## `pico_config()`
### Description
#### `pico_config(numChannels, direction, threshold, numSamples, inputVoltage, preTrigSamples, autoTrigMS, timebase)`
Configures the picoscope based on the given parameters. If a parameter or a combination of parameters is invalid, returns a string specifiying which parameter is invalid. If all parameters are valid, returns `"OK"`.
### Parameters
* `numChannels (int)` - the number of channels to record data from. `1 <= numChannels <= 4`
* `direction (string)` - a string representing the signal direction for a trigger to occur. Valid options are:
  * `"RISING"`
  * `"FALLING"`
  * `"ABOVE"`
  * `"BELOW"`
  * `"RISING_OR_FALLING"`
* `threshold (int)` - when the trigger should occur. `-32512 <= threshold <= 32512`
* `numSamples (int)` - the number of samples to collect. `1 <= numSamples <= 12655` 
* `inputVoltage (string)` - a string specifying the input voltage. Valid options are:
  * `"20MV"`
  * `"50MV"`
  * `"100MV"`
  * `"200MV"`
  * `"500MV"`
  * `"1V"`
  * `"5V"`
  * `"10V"`
  * `"20V"`
* `preTrigSamples (int)` - the number of samples to collect before the trigger occurs. `preTrigSamples <= numSamples`
* `autoTrigMS (int)` - how long the picoscope should wait in milliseconds before auto triggering
* `timebase (int)` - the timebase to use for data collection. affects sampling rate (lower value = higher sampling rate)
### Returns
If all parameters are valid, returns the string `"OK"`.
If a parameter is invalid, returns which parameter is invalid and a short description why.
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
Returns the actual sampling interval used by the picoscope. The returned value indicates how many nanoseconds pass between each sample.
### Parameters
None.
### Returns
Returns the actual sampling interval used by the picoscope.
