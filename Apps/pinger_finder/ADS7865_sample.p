#include "prustdlib.h"
#include "pingerFinderLib.h"

// Define all inputs
#define BUSY    15 // P8-15

// Define all output
#define bCONVST 15 // P8-11
#define bWR     14 // P8-12

// Define all GPIO
#define DB11    0  // P9-31


//-----------------------------------------------

.origin 0
.entrypoint START

// r0: Timeout counter
// r1: Advance bit coming from PRU1
// r2: Ptr to DRAM[0]

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

PREPARE:
        // Store data address for reference by the host program.
        //SBB_II DATA_MEM_START, samplestart_ptr, 1 

        LDI  DQ.PRU0_Ptr, 0x0000
        LDI  DQ.PRU1_Ptr, 0x2000

        MOV  DAQConf.TO, 0xBEBC200      // Ready up the timout counter
        MOV  r2, 0x2000                 // R2 points to DRAM1[0]

        MOV  DAQConf.Data_Dst, samplestart_ptr  // Determine where samples will go 
        MOV  DAQConf.Samp_Len, 10               // Set sample length to 10        

        // SET Default bits (to be deprecated by some outside script)
        SET  r30, bCONVST

TOP:
        QBLT SUBMIT, DQ.TapeHD_Offset, DAQConf.Samp_Len

        #ifdef TO_EN
        QBEQ END, DAQConf.TO, 0         // Check Timeout ctr. End program if too long.  
         DECR  DAQConf.TO, 1          // decrement timer.
        #endif

TRIG:
        LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
        QBBC TRIG, DQ.PRU1_State, CINT  // Advance when PRU1 trigger interupt!
        CLR  r30, bCONVST               // Trigger a Conversion

WAIT:
        // connect bCONVST to BUSY pin in order to bypass this portion
        WBC  r31, BUSY                  // Watch for conversion to complete

COLLECT:
        SET  r30, bCONVST               // CONVST is no longer needed TAG=cleanup
        CLR  r30, bWR                   // Activate bWR

        SET  DQ.PRU0_State, COLL     // vvv
        SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
                                        // Share PRU State
                                        // ^ state: collecting

        MOV  GP.Cpr, r31                // collecting data: save local cpy of GPI
        QBBC ASK_PRU1, GP.Cpr, DB11     // ^ Meas bit 11... go on to next step
         SET DQ.Sample, 11

ASK_PRU1:
                                                        // vvv Wait for PRU1 to finish.
        LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
        QBBS ASK_PRU1, DQ.PRU1_State, COLL
        
        LBBO GP.Cpr, DQ.PRU1_Ptr, SHAREDh, 4       // collect PRU1s partial sample
        SET  r31, bWR

        QBBC MDB9, GP.Cpr, DB10
         SET DQ.Sample, 10
MDB9:
        QBBC MDB8, GP.Cpr, DB9
         SET DQ.Sample, 9
MDB8:
        QBBC MDB7, GP.Cpr, DB8
         SET DQ.Sample, 8
MDB7:
        QBBC MDB6, GP.Cpr, DB7
         SET DQ.Sample, 7
MDB6:
        QBBC MDB5, GP.Cpr, DB6
         SET DQ.Sample, 6
MDB5:
        QBBC MDB4, GP.Cpr, DB5
         SET DQ.Sample, 5
MDB4:
        QBBC MDB3, GP.Cpr, DB4
         SET DQ.Sample, 4
MDB3:
        QBBC MDB2, GP.Cpr, DB3
         SET DQ.Sample, 3
MDB2:
        QBBC MDB1, GP.Cpr, DB2
         SET DQ.Sample, 2
MDB1:
        QBBC MDB0, GP.Cpr, DB1
         SET DQ.Sample, 1
MDB0:
        QBBC NEXT, GP.Cpr, DB0
         SET DQ.Sample, 0

NEXT:
        QBA  SUBMIT


/////////////////////////////
        LBBO r1, r2, 0, 4       // Grab data from DRAM1[0]
        QBEQ TOP, r1, 0   // Loop as long as PRU1 didnt intervene
        QBA  END


         //INCR DAQ_State.TapeHD_Offset, 1  // increment tapeHD at end of loop.

SUBMIT:
END:
        SET  r30, bCONVST
        MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        HALT
