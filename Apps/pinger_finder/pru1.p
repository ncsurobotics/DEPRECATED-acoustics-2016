#include "prustdlib.h"
#include "pingerFinderLib.h"

.macro  INIT_TIMER
        // //Submit current time
        MOV  GP.Tmr, 8// INIT time... 8 instructions precede this one.
.endm

.macro  Wait_For_CINT_ACK
.mparam LABEL
        ADD  GP.Tmr, GP.Tmr, 5
        LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
        QBBS LABEL, DQ.PRU1_State, CINT
.endm

.macro  Wait_For_PRU0_COLL
.mparam LABEL
        ADD GP.Tmr, GP.Tmr, 5
        LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)
        QBBC LABEL, DQ.PRU0_State, COLL
.endm

.macro	Set_DR_On_PRU1
		LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
		SET  DQ.PRU1_State, DR
		SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
.endm

.macro  Set_CINT_On_PRU1
		LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
        SET  DQ.PRU1_State, CINT        // Start with CINT active        
        SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
.endm

.macro  Sample_Delay
.mparam LABEL
        INCR GP.Tmr, 2 
        QBLE LABEL, DAQConf.Samp_Rate, GP.Tmr
.endm

.macro  Get_Sample_Rate_From_PRU0
		LBBO DAQConf.Samp_Rate, DQ.PRU0_Ptr, HOST_SRh, SIZE(DAQConf.Samp_Rate)
.endm

.macro Set_COLL_Lo_On_PRU0
	LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
	CLR  DQ.PRU0_State, COLL	// vvv
	SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
                                // Share PRU State
                                // ^ state: not collecting
.endm

/////////////////////////////////////////////////
//               MAIN Program               /////
/////////////////////////////////////////////////

.origin 0
.entrypoint START

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

INIT:
        MOV  DQ.PRU0_Ptr, 0x2000
        MOV  DQ.PRU1_Ptr, 0x0000
        
        MOV  DQ.PRU1_State, 0 			// Init status register
		SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
		
		Get_Sample_Rate_From_PRU0// Obtain sample_rate information
		MOV	 DQ.Sub_Sample, 0	// Initialize starting sub_sample

	/////////////////////////////////////////////////
	//               MAIN Loop                  /////
	/////////////////////////////////////////////////

TOP:
        Set_CINT_On_PRU1		// Start with CINT active   
        MOV  DQ.Sample, 0		// Clear Sample register
  P1:
        Wait_For_CINT_ACK P1	// Wait for CINT to be Acknowledged
        
        // At this point, PRU0 will have cleared the CINT bit from PRU1s
        // status code, thus acknowledging the demand to bring CONVST low.
        // PRU1 will now re-initialize the conversion timer to 0, since 
        // it assumes that PRU0 will bring the conversion signal low in the
        // next couple of clock cycles or so.
        
        INIT_TIMER// Re-int timer
        
ASK_PRU0:
        Wait_For_PRU0_COLL ASK_PRU0

		// At this point, PRU0 has updated its status code to set
		// COLL=1. This means that the PRU0 has recognized that a conversion
		// has completed, and has also brought WR low in order to begin
		// reading data from the ADC. Now, PRU1 will join by reading its
		// GPI (connected to ADC DB[10:0]), and then submit that data to
		// PRU0's shared memory space so that it can concatenate the data
		// to a full 12 bit code. A "DR" (Data Ready) bit will be set in 
		// PRU1's status code in order to notify PRU0 that it can
		// move on to the concatenation part.

COLLECT:
        // SET  r30, DB1 // <---- for debugging vvv
        SBBO r31, DQ.PRU0_Ptr, SHAREDh, 4   // Submit GPI
        // CLR  r30, DB1 // <---- for debugging ^^^
        Set_COLL_Lo_On_PRU0  				// << prevents false triggers on pru1
		Sub_Sample_Controller ASK_PRU0
			// Sub_Sample_Controller will either make a shortcut to the ASK_PRU0
			// step, or go all the way back at the top of the cycle... depending
			// on the sub_sample that was just collected.
        
        //Set_DR_On_PRU1					// Set DR bit
        
CORRECT_TIME:
		ADD  GP.Tmr, GP.Tmr, 26 //25 instr. + 1 add instr. occur before this point.
        
WAIT:
		//ADD GP.Tmr, GP.Tmr, 2 //Make up for time spent doing other stuff 
        Sample_Delay WAIT
        QBA TOP

END:
        HALT
