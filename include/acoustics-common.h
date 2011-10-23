
#ifndef __ACOUSTICS_COMMON_H_
#define __ACOUSTICS_COMMON_H_

/* Valid delays and corresponding conversion rates
 * 
 *  32 238805
 *  36 225352
 *  40 213333
 *  44 202531
 *  48 192771
 *  52 183908
 *  56 175824
 *  60 168421
 *  64 161616
 *  68 155339
 *  72 149532
 *  76 144144
 *  80 139130
 *  84 134453
 *  88 130081
 *  92 125984
 *  96 122137
 * 100 118518
 * 104 115107
 * 108 111888
 * 112 108843
 * 116 105960
 * 120 103225
 * 124 100628
 */

/* Number of conversion per second */
#define SAMPLES_PER_SECOND (202531)

/* Number of samples from each channel to store in a single buffer */
#define SAMPLES_PER_BUFFER (10 * 1024)

/* ADC sample size (16 bits) */
#define SAMPLE_SIZE 2

/* Number of channels */
#define CHANNELS 4

#define BUFFER_SIZE (SAMPLES_PER_BUFFER * CHANNELS * SAMPLE_SIZE)

#endif // #ifndef __ACOUSTICS_COMMON_H_
