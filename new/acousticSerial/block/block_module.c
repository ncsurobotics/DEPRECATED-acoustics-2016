/**
 * To build this module, you must have the picoscope SDK installed.
 */
#include <Python.h>

#include <stdio.h>

#include <sys/types.h>
#include <string.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>

#include <libps2000a-1.1/ps2000aApi.h>
#ifndef PICO_STATUS
#include <libps2000a-1.1/PicoStatus.h>
#endif

////// These settings will be routinely modified //////
/** Number of samples to record */
#define NUM_SAMPLES 12000
/** 
 * The input voltage(?) With format: PS2000A_<#><units>
 * Available values/units:
 * 20, 50, 100, 200, 500 MV
 * 1, 2, 5, 10, 20 V
 * Example:
 *    PS2000A_50MV
 *    PS2000A_2V
 */
#define INPUT_VOLTAGE PS2000A_100MV
/** Default sample interval */
#define DEF_SAMPLE_INTERVAL 100
/** 
 * Specifies the untis used for sampling intervals with format: PS2000A_<units>
 * Note: Not all units may be supported. NS with sample interval set to 20 may
 *       be as low as our unit goes.
 * Available units:
 *    FS, PS, NS, US, MS, S
 */
#define TIME_UNITS PS2000A_NS

////// These settings will generally be unchanged //////
/** The number of channels we're working with */
#define NUM_CHANNELS 4
/** Direction of the trigger */
#define DEF_DIRECTION PS2000A_RISING
/** ADC threshold for trigger to occur */
#define THRESHOLD 6000
/** Number of samples to record before the trigger */  
#define PRE_TRIGGER_SAMPLES 0
/** Number of milliseconds before auto trigger */
#define AUTO_TRIG_MS 0

/** 
 * This is how picoscope does bool.
 * Could probably be translated to regular
 * true/false with stdbool.h in the future.
 */
typedef enum enBOOL
{
  FALSE, TRUE
} BOOL;

/**
 * Structure used for keeping track of config options
 */
typedef struct {
  /** Number of channels */
  int numChannels;
  /** Trigger direction */
  int direction;
  /** Trigger ADC count threshold (-32512 to 32512) */
  int threshold;
  /** Number of samples to collect after trigger */
  uint32_t numSamples;
  /** Input voltage */
  int inputVoltage;
  /** How often to sample between each time unit  */
  int32_t sampleInterval;
  /** Unit of time for sample interval */
  int timeUnits;
  /** Number of pre-trigger samples */
  int32_t preTriggerSamples;
} CONFIG;

/** Keeps track of debug mode */
static BOOL debug = FALSE;
/** Keeps track of whether the picoscope has already been initialized */
static BOOL initialized = FALSE;

/** Keeps track of whether block data is ready */
static BOOL g_ready = FALSE;

/** Keeps track of the timebase used. Assigned value is starting point */
static int g_timebase = 35;
/** Actual number of samples per channel */
static int g_maxSamples = 0;

/** This is where the data from the picoscope is ultimately stored  */
static int16_t **storeBuffers;
/** This is where the picoscope temporarily stores data */
static int16_t **dataBuffers;

/** Keeps track of configuration state */
static CONFIG conf = {
  // TODO: rename these constants to DEF_ (for default)
  NUM_CHANNELS,
  DEF_DIRECTION,
  THRESHOLD,
  NUM_SAMPLES,
  INPUT_VOLTAGE,
  DEF_SAMPLE_INTERVAL,
  TIME_UNITS,
  PRE_TRIGGER_SAMPLES
};

/*************ps2000aBlockReady*************
 *    THIS IS A SPECIAL CALLBACK FUNCTION USED FOR COLLECTING BLOCK DATA. The method can
 *    have any name, but must have these parameters and return type. More details can be 
 *    found in the picoscope API (A) under the name "ps2000aBlockReady"
 *
 *  @param handle the handle for the unit
 *  @param status the status of the unit when this method was called
 *  @param pParameter any extra parameters passed to ps2000aRunBlock()
\*****************************************/
void getData( int16_t handle, PICO_STATUS status, void * pParameter )
{
  printf( "." );
  if ( status != PICO_CANCELLED ) {
    g_ready = TRUE;
  }
}

/**
 * Checks to make sure the status of the picoscope is OK.
 * Exits the program if not.
 */
void checkStatus( PICO_STATUS status, int16_t handle ) 
{
  if ( status == PICO_OK ) {
    printf( "OK!\n" );
  } else {
    printf( "failed. Code: %d. Aborting...\n", status );
    if ( handle != -1 ) status = ps2000aCloseUnit( handle );
    initialized = FALSE;
    g_ready = FALSE;
    exit( 1 );
  }
}

/**
 * Configures the unit. Needs to be called before pico_init(), otherwise config settings
 * will not take effect. Some notes:
 *
 * direction: this is the rising/falling edge. the valid values are:
 *              0: ABOVE
 *              1: BELOW
 *              2: RISING
 *              3: FALLING
 *              4: RISING_OR_FALLING
 *
 * threshold: this is the ADC count to activate the trigger. -32512 to 32512 (16 bits*) is the range
 *            it uses, and what the values mean is dependent on inputVoltage. You can convert from 
 *            the 16 bit value to voltage using the formula:
 *              voltage = (inputVoltage * threshold / 32512)
 *            
 *            Example: if inputVoltage = 4 (200MV) then:
 *              200MV = (200MV * 32512) / 32512 (trigger occures at 200MV)
 *              100MV = (200MV * 16256) / 32512 (trigger occures at 100MV)
 *              ~49MV = (200MV *  8000) / 32512 (trigger occures at ~49MV)
 *
 *            Example: if inputVoltage = 8 (5V) then:
 *                 5V = (5V * 32512) / 32512 (trigger occures at    5V)
 *               2.5V = (5V * 16256) / 32512 (trigger occures at  2.5V)
 *              ~1.2V = (5V *  8000) / 32512 (trigger occures at ~1.2V)
 *
 *            *NOTE: technically 16 bits is -32768 to 32767, but for some reason the picoscope only
 *                   uses -32512 to 32512 for voltages
 *            
 * inputVoltage: this is the voltage and units for the incoming signal. this setting determines what
 *            the sample values trigger threshold mean (in terms of voltage). the valid values are:
 *              1: 20MV
 *              2: 50MV
 *              3: 100MV
 *              4: 200MV
 *              5: 500MV
 *              6: 1V
 *              7: 2V
 *              8: 5V
 *              9: 10V
 *             10: 20V
 *
 *            See threshold for examples of how it affects the trigger voltage.
 *
 * sampleInterval: this is the interval between samples based on the value of timeUnits
 *            
 *              Example: if timeUnits = 5 (S) and sampleInterval = 2 then:
 *                the picoscope would collect signal data once every 2 seconds
 *
 *              Example: if timeUnits = 2 (NS) and sampleInterval = 1 then:
 *                the picoscope would collect signal data once every 1 nanosecond
 *
 * timeUnits: this is the unit of time between each sample. the valid values are:
 *              0: FS
 *              1: PS
 *              2: NS
 *              3: US
 *              4: MS
 *              5: S
 *
 * @param numChannels number of channels to record
 * @param direction (trigger) the signal direction to look for to activate the trigger (0 to 4)
 * @param threshold (trigger) the signal threshold to activate the trigger (-32512 to 32512)
 * @param numSamples number of samples to record
 * @param inputVoltage input voltage type (1 to 10)
 * @param sampleInterval the interval between samples (based on time units)
 * @param timeUnits the time units to use for sampling (0 to 5)
 *
 * @return returns NULL if the arguments aren't valid, otherwise None.
 *
 * TODO: Consider returning different values based on cause of return.
 * TODO: Move setting debug parameter from pico_init to this function and CONFIG struct
 */
static PyObject* pico_config( PyObject* self, PyObject* args )
{
  if ( initialized ) {
    return Py_BuildValue("");
  }
  
  if ( !PyArg_ParseTuple( args, "iiiiiii", &conf.numChannels,
                                           &conf.direction,
                                           &conf.threshold,
                                           &conf.numSamples,
                                           &conf.inputVoltage,
                                           &conf.sampleInterval,
                                           &conf.timeUnits ) ) {
    return NULL;
  }
  
  return Py_BuildValue("s", "OK");
}

/**
 * Starts the picoscope unit, allocates memory for sample coolection, configures the channels'
 * data buffers, and sets up a simple trigger.
 *  
 * @param debug whether to log pico status to console
 *
 * @return the handle of the unit
 */
static PyObject* pico_init( PyObject* self, PyObject* args )
{
  
  if ( !PyArg_ParseTuple( args, "i", &debug ) ) {
    return NULL;
  }

  initialized = TRUE;

  storeBuffers = (int16_t **)calloc( conf.numSamples, conf.numChannels * sizeof( int16_t * ) );
  for ( int i = 0; i < conf.numChannels; ++i ) {
    storeBuffers[ i ] = (int16_t *)calloc( conf.numSamples, conf.numSamples * sizeof( int16_t ) );
  }
  dataBuffers = (int16_t **)calloc( conf.numSamples, conf.numChannels * sizeof( int16_t * ) );
  for ( int i = 0; i < conf.numChannels; ++i ) {
    dataBuffers[ i ] = (int16_t *)calloc( conf.numSamples, conf.numSamples * sizeof( int16_t ) );
  }
  
  int16_t handle = -1;
  PICO_STATUS status;
  
  if (debug) printf( "Opening unit..." );
  status = ps2000aOpenUnit( &handle, NULL );
  if (debug) { 
    checkStatus( status, handle );
    printf( "\n" );
  }
  
  // configures the channels and sets a simple trigger
  for ( int i = 0; i < conf.numChannels; ++i ) {
    if (debug) printf( "Setting up channel %d...", i ); 
    // handle, channel, 1=enable, DC, input voltage, range, offset
    printf( "Setting input voltage to %d\n", conf.inputVoltage );
    status = ps2000aSetChannel( handle, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 1, 
                                PS2000A_AC, conf.inputVoltage, 0 );
    if (debug) checkStatus( status, handle );

    // set up the trigger on channel i
    if ( i == 0 ) {
      if (debug) printf( "Setting trigger..." );
      // handle, enable, channel source, threshold, direction, delay, autoTrigger_ms
      status = ps2000aSetSimpleTrigger( handle, 1, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 
                                        conf.threshold, conf.direction, 0, AUTO_TRIG_MS );
      if (debug) checkStatus( status, handle );
    }

    // handle, channel, buffer, buffer length, segment index, downsample ratio mode
    // for segment index and downsample ratio mode, see the ps2000a series API
    if (debug) printf( "Configuring databuffer %d...", i );
    status = ps2000aSetDataBuffer( handle, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 
                                   dataBuffers[i], conf.numSamples, 0, PS2000A_RATIO_MODE_NONE );
    if (debug) checkStatus( status, handle );
  }
  
  
  // find a usable time interval. iterates through timebases until it finds one that is supported
  // by the unit. higher timebase = lower sampling rate
  while ( ps2000aGetTimebase( handle, g_timebase, conf.numSamples, &conf.sampleInterval, 0, 
          &g_maxSamples, 0 ) ) {
    g_timebase++;
  }
  
  if ( debug ) printf( "\ntimebase: %d | sampleInterval: %d | maxSamples: %d\n", 
                       g_timebase, conf.sampleInterval, g_maxSamples );

  return Py_BuildValue( "i", handle );
  
}

/** 
 * Tells the picoscope to begin data collection. Will wait for the trigger to occur 
 * before returning.
 *
 * @param handle the unit to get data from.
 *
 * @return a list of 4 lists of voltages
 */
static PyObject* pico_get_data( PyObject* self, PyObject* args )
{
  int handle;
  PICO_STATUS status;

  if ( !PyArg_ParseTuple( args, "i", &handle ) ) {
    return NULL;
  }

  if (debug) printf( "\n" );

  if (debug) printf( "Running block data collection..." );
  
  // handle, pretrigger samples, 
  // posttriggersamples, timebase, oversample (not used),
  // timeIndiposedMs, segment index, ps2000aBlockReady function pointer, pParameter
  status = ps2000aRunBlock( handle, conf.preTriggerSamples, 
                            conf.numSamples - conf.preTriggerSamples, g_timebase, 0,
                            NULL, 0, getData, NULL );
  if (debug) checkStatus( status, handle );
  
  if (debug) {
    printf("Retreiving data...");
    fflush( stdout );
  }
  
  // int numLoops = 0;
  // int totalIterations = 0;

  // busy wait for g_ready to be true
  while ( !g_ready ) usleep(0);
  
  if ( g_ready ) {
    // handle, start index, num samples, downsample ratio, downsample mode, segment index, overflow
    status = ps2000aGetValues( handle, 0, &conf.numSamples, 0, PS2000A_RATIO_MODE_NONE, 0, NULL );
  }
  
  if (debug) {
    checkStatus( status, handle );
    printf( "Sample interval used for this dataset: %d\n", conf.sampleInterval );
    printf( "\n" );
    printf( "Stopping unit...");
  }
  
  status = ps2000aStop( handle );
  if (debug) checkStatus( status, handle );

  // create a PyObject to use to pass back the collected data (for all channels)
  PyObject* channels = PyList_New( conf.numChannels );
  
  // populate the PyObject with the collected data
  if ( debug ) {
    printf( "Transferring data from channels to returned PyObject..." );
    fflush( stdout );
  }
  for ( int i = 0; i < conf.numChannels; ++i ) {
    // temp PyObject used to get data for a channel
    PyObject* channel = PyList_New( conf.numSamples );
    
    if ( debug ) {
      printf( "%d...", i );
      fflush( stdout );
    }

    for ( int j = 0; j < conf.numSamples; ++j ) {
      // copy the sample to the channel i at item j
      PyList_SetItem( channel, j, Py_BuildValue( "i", dataBuffers[ i ][ j ] ) );
      
      // go ahead and reset our buffer values to 0
      storeBuffers[ i ][ j ] = 0;
      dataBuffers[ i ][ j ] = 0;
    }

    // add the channel data to our returning PyObject
    PyList_SetItem( channels, i, channel );
  }
  if ( debug ) printf( "OK!\n");

  if ( debug ) printf( "Returning data.\n" );
  
  g_ready = FALSE;
  return channels;
}

/**
 * Closes the picoscope and frees memory. Should be called by the python script before closing.
 * 
 * @param handle the handle of the picoscope
 *
 * @return NULL if args aren't correct, otherwise None
 */
static PyObject* pico_close( PyObject* self, PyObject* args )
{
  int handle;
  PICO_STATUS status;

  if ( !PyArg_ParseTuple( args, "i", &handle ) ) {
    return NULL;
  }
  
  if (debug) printf( "Closing unit..." );
  status = ps2000aCloseUnit( handle );
  if (debug) checkStatus( status, handle );

  for ( int i = 0; i < conf.numChannels; ++i ) {
    free( storeBuffers[ i ] );
  }
  free( storeBuffers ); 
  for ( int i = 0; i < conf.numChannels; ++i ) {
    free( dataBuffers[ i ] );
  }
  free( dataBuffers );

  initialized = FALSE;
  g_ready = FALSE;

  return Py_BuildValue("");
}

static PyObject* pico_get_sample_interval( PyObject* self, PyObject* args )
{
  return Py_BuildValue( "i", conf.sampleInterval );
}

/**
 * The functions for this module
 */
static PyMethodDef PicoMethods[] =
{
  { "pico_config", pico_config, METH_VARARGS, "configures the picoscope. to be called before pico_init" },
  { "pico_init", pico_init, METH_VARARGS, "initializes the picoscope unit" },
  { "pico_get_data", pico_get_data, METH_VARARGS, "gets the next set of data from the picoscope" },
  { "pico_close", pico_close, METH_VARARGS, "closes the picoscope unit" },
  { "pico_get_sample_interval", pico_get_sample_interval, METH_VARARGS, "gets the interval between samples (nano seconds)" },
};

/**
 * python 2.7 initialization function
 */
PyMODINIT_FUNC
initpico_module( void )
{
  ( void ) Py_InitModule( "pico_module", PicoMethods );
}
