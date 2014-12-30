// r0: Timeout counter
// r1: Advance bit coming from PRU1
// r2: Ptr to DRAM[0]

// r0: GP Ptr
// r1: GP Tmr
// r2: Reserved
// r3: Reserved
// r4: DAQ_State
// r5: DAQ_Config
// r6: DAQ_Config
// r7: DAQ_Config
// r8: DAQ_Config

#define TO_EN

.struct General
	.u32	Ptr
	.u32	Tmr
	.u32	Cpr
.ends	
.assign General, r0, r2, GP


.struct DAQ_State
	.u16	TapeHD_Offset
	.u8	PRU0_State
	.u8	PRU1_State
.ends
.assign DAQ_State, r5, r5, DAQState


.struct DAQ_Config
	.u32	Samp_Len	// samples
	.u32	Samp_Rate	// loops
	.u32	Data_Dst	// address 
	.u32	TO		// TimeOut:loops
.ends
.assign DAQ_Config, r6, r9, DAQConf
