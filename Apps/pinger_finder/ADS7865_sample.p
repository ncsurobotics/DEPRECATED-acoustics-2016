#include "prustdlib.h"
#include "pingerFinderLib.h"


.macro  Wait_For_COLL_CLR_Signal
.mparam LABEL
		LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)
		QBBS LABEL, DQ.PRU0_State, COLL
.endm
	
.macro  Conf_DataDst_For_DDR_Address
		LBBO DAQConf.Data_Dst, DQ.PRU0_Ptr, HOST_DDR_ADDRh, 4 
.endm

.macro  Conf_DataDst_For_Local_Ram_Address
		#define samplestart_ptr 0x0007 //cells from 0 (8bit = 1byte)
			// 0x0007 use to represent the end of PRU ram dedicated
			// to settings... so this was once designating the location \
			// be begine writing ADC samples to in PRU RAM. Since then, it was 
			// chosen to write sample to DDRAM instead, and now this macro is
			// not used in the code anywhere. It should be deleted at some 
			// convenient time soon
		MOV  DAQConf.Data_Dst, samplestart_ptr
.endm

.macro  Get_SL
		LBBO DAQConf.Samp_Len, DQ.PRU0_Ptr, HOST_SLh, 4
.endm 

.macro  Set_COLL_High_On_PRU0
	LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
	SET  DQ.PRU0_State, COLL	// vvv
	SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
                                // Share PRU State
                                // ^ state: collecting
.endm



//-----------------------------------------------

.origin 0
.entrypoint START

// r0: Timeout counter
// r1: Advance bit coming from PRU1
// r2: Ptr to DRAM[0]

START:
	LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
	CLR  r0, r0, 4	  // Clear bit 4 in reg 0
	SBCO r0, C4, 4, 4       // Store Bytes Constant Offset
	
	ZERO &r0, 122

PREPARE:
	LDI  DQ.PRU0_Ptr, 0x0000		// Init PRU0 ptr
	LDI  DQ.PRU1_Ptr, 0x2000		// Init PRU1 ptr
	
	MOV  DQ.PRU0_State, 0 			// Init status register
	SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)

	MOV  DAQConf.TO, 0xBEBC200		// Init timout counter
	MOV  r2, 0x2000					// R2 points to DRAM1[0]

	Conf_DataDst_For_DDR_Address	// Data will go to DDRAM.
	Get_SL							// Receive SL from HOST.
	MOV	 DQ.Sub_Sample, 0			// Known that first sample is sub_sample 0
	//MOV  DAQConf.Samp_Len, 35		// Set sample length to 10	
	

	// SET Default bits (to be deprecated by some outside script)
	SET  r30, bCONVST

TOP:
	// DQ.TapeHD_Offset: variable representing the current position/offset of
	// the pointer writing to DDRAM. Once DQ.TapeHD_Offset > DAQConf.Samp_Len,
	// we know that we have collected all the samples that the user has requested,
	// and the program will end. 
	//   NOTE: DQ.TapeHD_Offset must increment in steps of 4, as DDRAM is only 32 bit
	//   addressable.
	
	// DAQConf.Samp_Len: Variable that represents n_samples_requested*4.
	QBLT END, DQ.TapeHD_Offset, DAQConf.Samp_Len

	#ifdef TO_EN
	QBEQ END, DAQConf.TO, 0		// Check Timeout ctr. End program if too long.  
	 DECR DAQConf.TO, 1			// decrement timer.
	#endif

TRIG:
	LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
	QBBC TRIG, DQ.PRU1_State, CINT	// Advance when PRU1 trigger interupt!
	CLR	 DQ.PRU1_State, CINT
	SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)

CONVST:	
	CLR  r30, bCONVST				// Trigger a Conversion

WAIT:
	// connect bCONVST to BUSY pin in order to bypass this portion
	NOP32; NOP32;	// delay just in case
	WBC  r31, BUSY		// Watch for conversion to complete
	
	// At this point, PRU0 has detected BUSY go low. Thus, a conversion
	// has been completed, and a data point is ready for collection.
	// PRU0 will now pull WR low (+ deactivate CONVST) in order to
	// get the ADC output the 12-bit sample. Then it will set it's
	// COLL=1 in the PRU0 status code, which should notify PRU1 that
	// it should join in on the sample collection process.
	

COLLECT:
	SET  r30, bCONVST	// CONVST is no longer needed TAG=cleanup
	CLR  r30, bRD		// Activate bWR

	Set_COLL_High_On_PRU0	// << Used to signal PRU1 to sample ADC

ASK_PRU1:
	Wait_For_COLL_CLR_Signal	ASK_PRU1       // << Wait for PRU1 to finish sampling.
	LBBO GP.Cpr, DQ.PRU0_Ptr, SHAREDh, 4       // << Collect PRU1s partial sample.
	SET  r31, bWR

	// At this point, PRU1s measurement has been received, and PRU0
	// has done the necessary cleanup (DR:=0, bWR:=1, COLL:=0(By PRU1). 
	// Now, PRU0 will parse the collected sample and convert it to an 
	// intelligible format.
	
	MOV  DQ.Sample, 0		// re-init the sample reg
MDB11:
	QBBC MDB10, GP.Cpr, DB11   
	 SET DQ.Sample, 11
MDB10:
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


SUBMIT:
	SBBO DQ.Sample, DAQConf.Data_Dst, DQ.TapeHD_Offset, SIZE(DQ.Sample) // submit data to DDR
	INCR DQ.TapeHD_Offset, 4 // increment pointer
	
	Sub_Sample_Controller CONVST
		// Sub_Sample_Controller will either make a shortcut to the CONVST
		// step, or go all the way back at the top of the cycle... depending
		// on the sub_sample that was just collected.
	
	QBA	 TOP// loop back to Top Branch instruction
	
END:
	MOV  GP.Cpr, 0
	SBBO GP.Cpr, DAQConf.Data_Dst, DQ.TapeHD_Offset, SIZE(DQ.Sample) // submit data to DDR
	SET  r30, bCONVST
	MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
	HALT
