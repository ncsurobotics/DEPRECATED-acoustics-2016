/**
 * \file 
 * \brief Acoustics parameters and definitions
 */

#ifndef __SEAWOLF3_ACOUSTICS_INCLUDE_H
#define __SEAWOLF3_ACOUSTICS_INCLUDE_H

#include <math_bf.h>
#include <complex_bf.h>

#include "acoustics-common.h"

/**
 * \defgroup parameters Parameters
 * \ingroup userspace
 * \brief Userspace parameters and constants
 * \{
 */

/** Channel A (hydrophone 4) */
#define A 0

/** Channel B (hydrophone 3) */
#define B 1

/** Channel C (hydrophone 2) */
#define C 2

/** Channel D (hydrophone 1) */
#define D 3

#define DUMP(x) (1 << (x))

/** Number of kernel buffers to keep in each channels circular buffer */
#define CIR_BUFFER_KBUFFER_COUNT 4

/** Total number of samples in each channel's circular buffer */
#define CIR_BUFFER_SIZE (SAMPLES_PER_BUFFER * CIR_BUFFER_KBUFFER_COUNT)

/** Minimum triggering value (raw value) */
#define TRIGGER_VALUE ((float)(.0001))

/** Number of samples to offset the position of the trigger by. This is used to
    better center the trigger in the sample */
#define TRIGGER_POINT_OFFSET 200

/** Use this channel to detect the incoming signal (i.e. trigger on) */
#define TRIGGER_CHANNEL A

/** The correlation block only acts on a subset of the available data. Namely,
    points within +/- CORR_RANGE of the trigger point. This parameter can be
    used to tune the amount of the data the correlation block is run over */
#define CORR_RANGE 512

/** The correlation block will only consider lag values from -COR_LAG_MAX to
    COR_LAG_MAX */
#define CORR_LAG_MAX 60 

/** Divide each data point in the cross correlation by this factor */
#define CORR_SCALE_FACTOR 2

/** Data out of the FIR filter block may not be centered at 0, so after
    filtering, each data block is zeroed by shifting the signal by the signal
    mean. The mean is calculated by averaging this many samples at the beginning
    of the block */
#define AVG_COUNT 100

/* Circular buffer states */

/** Data blocks are being read in and possibly searched for a ping (trigger) */
#define READING   0x00

/** A ping (trigger) has been located. Procede to padding out the circular buffer */
#define TRIGGERED 0x01

/** The collected data is ready for filtering and correlation */
#define DONE      0x02

/** Additional blocks to read once triggered (see \ref TRIGGERED). This is used
    to ensure that the full ping waveform is present in all channels */
#define EXTRA_READS 1

/* Profiling helpers */
#ifdef ACOUSTICS_PROFILE
# define TIME_PRE(t, text) do {                    \
        printf("%-30s", (text));                   \
        fflush(stdout);                            \
        Timer_reset(t);                            \
    } while(false)
# define TIME_POST(t) do {                      \
        printf("%5.3f\n", Timer_getDelta(t));   \
    } while(false)
#else
# define TIME_PRE(t, text) do { } while(false)
# define TIME_POST(t) do { } while(false)
#endif

/** \} */

/* Support routines */
fract16* load_coefs(char* coef_file_name, int* num_coefs);
int find_max_cmplx(complex_fract16* w, int size);
void multiply(complex_fract16* in1, complex_fract16* in2, complex_fract16* out, int size);
void conjugate(complex_fract16* w, int size);

void populate_ideal_signal();
int crosscor_max(fract16* a, fract16* b, int size, int min_lag, int max_lag);
#endif // #ifndef __SEAWOLF3_ACOUSTICS_INCLUDE_H
