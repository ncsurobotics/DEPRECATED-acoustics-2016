#include "prustdlib.h"
#include "pingerFinderLib.h"

.macro  INIT_TIMER
        // //Submit current time
        MOV  GP.Tmr, 0// INIT time
.endm

.macro  Wait_For_CINT_ACK
.mparam LABEL
        ADD  GP.Tmr, GP.Tmr, 5
        LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
        QBBC LABEL, DQ.PRU1_State, CINT
.endm

.macro  Wait_For_PRU0_COLL
.mparam LABEL
        ADD GP.Tmr, GP.Tmr, 5
        LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)
        QBBS LABEL, DQ.PRU0_State, COLL
.endm

.origin 0
.entrypoint START

.macro  Sample_Delay
.mparam LABEL
        INCR GP.Tmr, 2 
        QBLE LABEL, DAQConf.Samp_Rate, GP.Tmr
.endm

// r1: Data to put in DRAM[0]
// r2: Ptr to DRAM[0]

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

        //MOV  r1, 1              // Setup bit be pru1 ack bit
        //MOV  r2, 0x0000         // address to DRAM1[0]
        //SBBO r1, r2, 0, 4       // Store data in DRAM1[0]


INIT:
        MOV  DQ.PRU0_Ptr, 0x2000
        MOV  DQ.PRU1_Ptr, 0x0000

TOP:
        SET  DQ.PRU1_State, CINT        // Start with CINT active        
        SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)

        MOV  DQ.Sample, 0               // Clear Sample register
  P1:
        Wait_For_CINT_ACK P1            // Wait for CINT to be Acknoledged
        INIT_TIMER// Re-int timer
        
ASK_PRU0:
        Wait_For_PRU0_COLL ASK_PRU0

COLLECT:
        SBBO r31, DQ.PRU0_Ptr, SHAREDh, 4       // Submit GPI
WAIT:
        Sample_Delay WAIT
        QBA TOP
        //SET  DQ.PRU1_State, PRU_BUSY// DONE! Notify PRU0
        //SBBO DQ.PRU1_State, DQ.PRU1_Ptr, 0, SIZE(DQ.PRU1_State)// ^^

END:
        HALT
