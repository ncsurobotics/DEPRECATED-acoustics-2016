// *****************************************************************************/
// file:   pru-stdlib.hp
//
// brief:  Commonly used constants for PRU work.
//
//
//  (C) Copyright 2012, Texas Instruments, Inc
//
//  author     J. Smith
//
//  version    0.1     Created
// *****************************************************************************/

#ifndef _prustdlib_HP_
#define _prustdlib_HP_

// ***************************************
// *      Global Macro definitions       *
// ***************************************

// Refer to this mapping in the file - \prussdrv\include\pruss_intc_mapping.h
#define PRU0_PRU1_INTERRUPT     17
#define PRU1_PRU0_INTERRUPT     18
#define PRU0_ARM_INTERRUPT      19
#define PRU1_ARM_INTERRUPT      20
#define ARM_PRU0_INTERRUPT      21
#define ARM_PRU1_INTERRUPT      22

#define CONST_PRUDRAM   C24
#define CONST_L3RAM     C30
#define CONST_DDR       C31


#define CONTROL_MODULE          0x44e10800

.macro  LD32
.mparam dst,src
    LBBO    dst,src,#0x00,4
.endm

.macro  LD16
.mparam dst,src
    LBBO    dst,src,#0x00,2
.endm

.macro  LD8
.mparam dst,src
    LBBO    dst,src,#0x00,1
.endm

.macro ST32
.mparam src,dst
    SBBO    src,dst,#0x00,4
.endm

.macro ST16
.mparam src,dst
    SBBO    src,dst,#0x00,2
.endm

.macro ST8
.mparam src,dst
    SBBO    src,dst,#0x00,1
.endm

// ------
// given an "offset" (some value b/t 0x000 and 0xFFF), this
// macro will configure the appropiate mux to a particular
// 32-bit "value"
.macro  SET_MUX
.mparam offset, value
        MOV  r25, CONTROL_MODULE | offset
	MOV  r26, value
        SBBO r26, r25, 0, 4
.endm

.macro  SBB_II
.mparam src_I, dst_I, size
        MOV r26, dst_I
        MOV r25, src_I
        SBBO r25, r26, 0, size
.endm

.macro	INCR
.mparam ctrReg, stepSize
	ADD ctrReg, ctrReg, stepSize
.endm

.macro	DECR
.mparam ctrReg, stepSize
	SUB ctrReg, ctrReg, stepSize
.endm

.macro  WBCR 
.mparam Label, Reg, Ptr, L
	LBBO Reg, Ptr, 0, SIZE(Reg)
	QBBC Label, Reg, L
.endm

// ***************************************
// *    Global Structure Definitions     *
// ***************************************


// ***************************************
// *     Global Register Assignments     *
// ***************************************


#endif // _pru-stdlib_HP_
