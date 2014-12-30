#include "prustdlib.hp"
#include "pingerFinderLib.h"

// Define all inputs
#define BUSY    15 // P8-15

// Define all output
#define bCONVST 15 // P8-11
#define bWR     14 // P8-12

// Define all GPIO
#define DB11    0  // P9-31

// Define Memory settings
#define PERMA_MEM_START 0x0000
#define PERMA_MEM_SIZE  0x0008
#define VOLAT_MEM_START PERMA_MEM_START+PERMA_MEM_SIZE
#define VOLAT_MEM_SIZE  0x0008
#define DATA_MEM_START  VOLAT_MEM_START+VOLAT_MEM_SIZE

// Define Memory based struct stuff
#define point_loc_ptr   0x0000 //counts (1byte)
#define samplen_ptr     0x0001 //counts (12bit = 1.25bytes)
#define delaylen_ptr    0x0003 //clk_cycles (32bit = 4bytes)
#define samplestart_ptr 0x0007 //cells from 0 (8bit = 1byte)


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

        MOV  DAQConf.TO, 0xBEBC200      // Ready up the timout counter
        MOV  r2, 0x2000         // R2 points to DRAM1[0]
        MOV  DAQConf.Data_Dst, samplestart_ptr  // Determine where samples will go 
        MOV  DAQConf.Samp_Len, 10               // Set sample length to 10        

        // SET Default bits (to be deprecated by some outside script)
        CLR  r30, bCONVST

TOP:
        QBGT SUBMIT, DAQState.TapeHD_Offset, DAQConf.Samp_Len

        #ifdef TO_EN
        QBEQ END, DAQConf.TO, 0         // Check Timeout ctr. End program if too long.  
         DECR  DAQConf.TO, 1          // decrement timer.
        #endif

        SET  r30, bCONVST       // 
        LBBO r1, r2, 0, 4       // Grab data from DRAM1[0]
        QBEQ TOP, r1, 0   // Loop as long as PRU1 didnt intervene
        QBA  END


         //INCR DAQ_State.TapeHD_Offset, 1  // increment tapeHD at end of loop.

SUBMIT:
END:
        CLR  r30, bCONVST
        MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        HALT
