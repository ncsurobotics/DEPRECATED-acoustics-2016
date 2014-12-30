#include "prustdlib.hp"
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
        SBB_II DATA_MEM_START, samplestart_ptr, 1 

        MOV  DAQState.PRU0_State_Ptr, 0x0000
        MOV  DAQState.PRU1_State_Ptr, 0x2000

        MOV  DAQConf.TO, 0xBEBC200      // Ready up the timout counter
        MOV  r2, 0x2000         // R2 points to DRAM1[0]

        MOV  DAQConf.Data_Dst, samplestart_ptr  // Determine where samples will go 
        MOV  DAQConf.Samp_Len, 10               // Set sample length to 10        

        // SET Default bits (to be deprecated by some outside script)
        SET  r30, bCONVST

TOP:
        QBGT SUBMIT, DAQState.TapeHD_Offset, DAQConf.Samp_Len

        #ifdef TO_EN
        QBEQ END, DAQConf.TO, 0         // Check Timeout ctr. End program if too long.  
         DECR  DAQConf.TO, 1          // decrement timer.
        #endif

TRIG:
        CLR  r30, bCONVST       // Trigger a Conversion

WAIT:
        // connect bCONVST to BUSY pin in order to bypass this portion
        WBC  r31, BUSY          // Watch for conversion to complete

COLLECT:
        SET  r30, bCONVST       // CONVST is no longer needed TAG=cleanup
        CLR  r30, bWR           // Activate bWR

        SET  DAQState.PRU0_State, Col_Act // Notify PRU1
        MOV  GP.Ptr, 0x2000      
        SBBO DAQState.PRU0_State, GP.Ptr, 0, SIZE(DAQState.PRU0_State)

        MOV  GP.Cpr, r31                // collecting data: save local cpy of GPI
        QBBC ASK_PRU1, GP.Cpr, DB11     // ^ Meas bit 11... go on to next step
         SET DAQState.Sample, 11

ASK_PRU1:
                                                        // vvv Wait for PRU1 to finish.
        LBBO DAQState.PRU1_State, DAQState.PRU1_State_Ptr, 0, SIZE(DAQState.PRU1_State)
        QBBS ASK_PRU1, DAQState.PRU1_State, Col_Act
        
        LBBO GP.Cpr, DAQState.PRU1_Ptr, SHARED, 4       // collect PRU1s partial sample
        OR   DAQ_State.Sample, DAQ_State.Sample, GP.Cpr // append data to sampling

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
