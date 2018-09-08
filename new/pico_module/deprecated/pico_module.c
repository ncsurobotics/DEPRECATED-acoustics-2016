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

#include <libps2000a-1.1/ps2000aApi.h>
#ifndef PICO_STATUS
#include <libps2000a-1.1/PicoStatus.h>
#endif

/** The number of channels we're working with */
#define NUM_CHANNELS 4
/** Direction of the trigger */
#define DEF_DIRECTION PS2000A_RISING
/** ADC threshold for trigger to occur */
#define THRESHOLD 3000
/** Number of samples to record */
#define NUM_SAMPLES 50000
/** 
 * The input voltage(?) With format: PS2000A_<#><units>
 * Available values/units:
 * 20, 50, 100, 200, 500 MV
 * 1, 2, 5, 10, 20 V
 * Example:
 *    PS2000A_50MV
 *    PS2000A_2V
 */
#define INPUT_VOLTAGE PS2000A_5V
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
/** Number of samples to record before the trigger */  
#define PRE_TRIGGER_SAMPLES 0



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
  int numSamples;
  /** Input voltage */
  int inputVoltage;
  /** How often to sample between each time unit  */
  unsigned int sampleInterval;
  /** Unit of time for sample interval */
  int timeUnits;
} CONFIG;

/** Global variable to keep track of autostop */
static int16_t g_autoStop = FALSE;
/** Global variable to keep track of trigger status */
static int16_t g_triggered = FALSE;
/** Global variable ot keep track of total number of samples collected */
static unsigned int g_samplesCollected = 0;
/** This is where the data from the picoscope is ultimately stored  */
static int16_t **storeBuffers;
/** This is where the picoscope temporarily stores data */
static int16_t **dataBuffers;
/** Keeps track of debug mode */
static BOOL debug = FALSE;
/** Keeps track of whether the picoscope has already been initialized */
static BOOL initialized = FALSE;
/** Global variable to keep track of the current position in storeBuffer */
static unsigned int nextStoreIndex = 0;
/** Keeps track of configuration state */
static CONFIG conf = {
  // TODO: rename these constants to DEF_ (for default)
  NUM_CHANNELS,
  DEF_DIRECTION,
  THRESHOLD,
  NUM_SAMPLES,
  INPUT_VOLTAGE,
  DEF_SAMPLE_INTERVAL,
  TIME_UNITS  
};

/***********ps2000aStreamingReady***********
 *    THIS IS A SPECIAL CALLBACK FUNCTION USED FOR SAMPLING DATA. It can have any name, 
 *    but must have these parameters and return type. More details can be found in the
 *    picoscope API (A) under the name "ps2000aStreamingReady"
 *
 *  handle:      device identifier
 *  noOfSamples: number of samples to collect
 *  startIndex:  an index to the first valid sample in the buffer that was passed in
 *               ps2000aSetDataBuffer
 *  overflow:    returns a set of flags that indecate whether an overvoltage has occured
 *               on any of the channels
 *  triggerAt:   an index to the buffer indicating the location of the trigger point relative
 *               to startIndex. Only valid when triggered is non-zero
 *  triggered:   a flag indicated whether a trigger occured. If non-zero, a trigger occured at
 *               the location indicated by triggerAt
 *  autoStop:    the flag that was set in the call to ps2000aRunStreaming
 *  *pParameter: a void pointer passed from ps2000aGetStreamingLatestValues. The callback
 *               can write to this location to send an data, such as a status flag, back to
 *               the application
 \*****************************************/
void getData
(
    int16_t   handle, 
    int32_t   noOfSamples, 
    uint32_t  startIndex,
    int16_t   overflow,
    uint32_t  triggerAt,
    int16_t   triggered,
    int16_t   autoStop,
    void      *pParameter
)
{
  if ( triggered ) g_triggered = TRUE;
  g_autoStop = autoStop;
  unsigned int copied = triggered ? noOfSamples - triggerAt : noOfSamples;
  
  if ( triggered && debug ) printf( "trigger hit...%d...", startIndex + triggerAt );

  for ( int i = 0; i < NUM_CHANNELS; ++i ) {  
    if ( triggered && debug && i == 0 ) {
      printf( "\n+------------+------------+--[TRIGGER]-+------------+------------+\n" );
      printf( "| %10s | %10s | %10s | %10s | %10s |\n", "CHANNEL", "COPIED", "FROM", "TO", "TOTAL" );
      printf( "+------------+------------+------------+------------+------------+\n" );
    }
    
    if ( g_triggered ) {
      unsigned int from = triggered ? triggerAt + startIndex : startIndex;
      unsigned int to = nextStoreIndex;
      unsigned int total = g_samplesCollected;
      if ( debug ) printf( "| %10d | %10d | %10d | %10d | %10d |\n", i, copied, from, to, total );
      memcpy( &storeBuffers[ i ][ to ], &dataBuffers[ i ][ from ], copied * sizeof( int16_t ) );
    }
  }
  
  if ( g_triggered ) {
   f ( debug ) printf( "%d, %d\n", nextStoreIndex, g_samplesCollected );
   g_samplesCollected += copied;
    nextStoreIndex += copied;
  }
}

/**
 * Checks to make sure the status of the picoscope is OK.
 * Exits the program if not.
 *
 * TODO: should probably pass in the handle and try to close
 * if before exiting.
 */
void checkStatus( PICO_STATUS status ) 
{
  if ( status == PICO_OK ) {
    printf( "OK!\n" );
  } else { 
    printf( "failed. Code: %d. Aborting...\n", status );
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
 *              Example: if timeUnits = 2 (NS) and sampleIntervnal = 1 then:
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
  
  nextStoreIndex = 0;
  g_samplesCollected = 0;

  if ( debug ) printf( "%d, %d\n", nextStoreIndex, g_samplesCollected );

  storeBuffers = (int16_t **)calloc( conf.numSamples, conf.numChannels * sizeof( int16_t * ) );
  for ( int i = 0; i < conf.numChannels; ++i ) {
    storeBuffers[ i ] = (int16_t *)calloc( conf.numSamples, conf.numSamples * sizeof( int16_t ) );
  }
  dataBuffers = (int16_t **)calloc( conf.numSamples, conf.numChannels * sizeof( int16_t * ) );
  for ( int i = 0; i < conf.numChannels; ++i ) {
    dataBuffers[ i ] = (int16_t *)calloc( conf.numSamples, conf.numSamples * sizeof( int16_t ) );
  }
  
  int16_t handle;
  PICO_STATUS status;
  
  if (debug) printf( "Opening unit..." );
  status = ps2000aOpenUnit( &handle, NULL );
  if (debug) { 
    checkStatus( status );
    printf( "\n" );
  }

  // configures the channels and sets a simple trigger
  for ( int i = 0; i < conf.numChannels; ++i ) {
    if (debug) printf( "Setting up channel %d...", i ); 
    // handle, channel, 1=enable, DC, input voltage, range, offset
    printf( "Setting input voltage to %d\n", conf.inputVoltage );
    status = ps2000aSetChannel( handle, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 1, 
                                PS2000A_AC, conf.inputVoltage, 0 );
    if (debug) checkStatus( status );

    if ( i == 0 ) {
      if (debug) printf( "Setting trigger..." );
      // handle, enable, channel source, threshold, direction, delay, autoTrigger_ms
      status = ps2000aSetSimpleTrigger( handle, 1, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 
                                        conf.threshold, conf.direction, 0, 4000 );
      if (debug) checkStatus( status );
    }

    // handle, channel, buffer, buffer length, segment index, downsample ratio mode
    // for segment index and downsample ratio mode, see the ps2000a series API
    if (debug) printf( "Configuring databuffer %d...", i );
    status = ps2000aSetDataBuffer( handle, (PS2000A_CHANNEL)(PS2000A_CHANNEL_A + i), 
                                   dataBuffers[i], conf.numSamples, 0, PS2000A_RATIO_MODE_NONE );
    if (debug) checkStatus( status );
  }


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

  // handle, sample interval, interval time units, max pre-trigger samples, max post, autoStop(?),
  //    downsample ratio, DS ratio mode, overview buffer size
  // time interval: this function changes time interval to what it ACTUALLY did
  // autoStop: automatically stops sampling when "maxSamples"(?) has been captured
  if (debug) printf( "Starting data collection..." );
  // TODO: add configuration option for maximum pre trigger samples to record
  status = ps2000aRunStreaming( handle, &conf.sampleInterval, conf.timeUnits, 
                                PRE_TRIGGER_SAMPLES, conf.numSamples - PRE_TRIGGER_SAMPLES, 
                                TRUE, 1, PS2000A_RATIO_MODE_NONE, conf.numSamples );
  if (debug) checkStatus( status );
  
  if (debug) {
    printf("Retreiving data...");
    fflush( stdout );
  }

  int numLoops = 0;
  int totalIterations = 0;
  // Keeps getting data until autoStop has been hit. This makes sure that ALL the data is
  // collected.
  while ( !g_autoStop ) {
    if ( debug && !g_triggered && numLoops++ % 10000 == 0 ) printf( "." );
    
    // the NULL value here is a parameter pointer that the getData function MAY use
    // to return information back to this one (here it is unused)
    status = ps2000aGetStreamingLatestValues( handle, getData, NULL );

    if ( numLoops == 10000 ) {
      numLoops = 0;
      totalIterations++;
    }
    fflush( stdout );
    if ( totalIterations > 800 ) {
      if ( debug ) printf( "Too many loops. Stopping...\n" );
      g_autoStop = TRUE;
    }
  }
  
  if (debug) {
    checkStatus( status );
    printf( "Sample interval used for this dataset: %d\n", conf.sampleInterval );
    printf( "Total number of samples collected: %d\n", g_samplesCollected );
    printf( "\n" );
    printf( "Stopping unit...");
  }
  
  status = ps2000aStop( handle );
  if (debug) checkStatus( status );

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
      PyList_SetItem( channel, j, Py_BuildValue( "i", storeBuffers[ i ][ j ] ) );
      
      // go ahead and reset our buffer values to 0
      storeBuffers[ i ][ j ] = 0;
      dataBuffers[ i ][ j ] = 0;
    }

    // add the channel data to our returning PyObject
    PyList_SetItem( channels, i, channel );
  }
  printf( "OK!\n");
  
  nextStoreIndex = 0;
  g_autoStop = FALSE;
  g_triggered = FALSE;
  g_samplesCollected = 0;
  if ( debug ) printf( "Returning data.\n" );
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
  if (debug) checkStatus( status );

  for ( int i = 0; i < conf.numChannels; ++i ) {
    free( storeBuffers[ i ] );
  }
  free( storeBuffers ); 
  for ( int i = 0; i < conf.numChannels; ++i ) {
    free( dataBuffers[ i ] );
  }
  free( dataBuffers );

  initialized = FALSE;
  nextStoreIndex = 0;
  g_autoStop = FALSE;
  g_triggered = FALSE;
  g_samplesCollected = 0;

  return Py_BuildValue("");
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
};

/**
 * python 2.7 initialization function
 */
PyMODINIT_FUNC
initpico_module( void )
{
  ( void ) Py_InitModule( "pico_module", PicoMethods );
}
