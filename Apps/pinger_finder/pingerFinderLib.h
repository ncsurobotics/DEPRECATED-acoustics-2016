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



/////////////////////////////////////////
// 		SETTINGS 	/////////
/////////////////////////////////////////
//#define TO_EN

/////////////////////////////////////////
// 		STRUCTS 	/////////
/////////////////////////////////////////
.struct General
	.u32	Ptr
	.u32	Tmr
	.u32	Cpr
.ends	
.assign General, r0, r2, GP

// bit0: BUSY
// bit1: ON STBY
// bit2: Collecting Data
// bit3: Tmr Interrupt
#define COLL	2 // Collection active bit
#define CINT    3 // CONVST interrupt bit
//#define DR		4 // Data Ready Bit
.struct DAQ_State
	.u32	Sample
	.u32	PRU0_Ptr
	.u32	PRU1_Ptr
	.u16	TapeHD_Offset
	.u8	PRU0_State
	.u8	PRU1_State
	.u8 	Sub_Sample //0 or 1... as ADC always grabs two channels at a time. 
.ends
.assign DAQ_State, r5, r9.b0, DQ


.struct DAQ_Config
	.u32	Samp_Len	// samples
	.u32	Samp_Rate	// loops
	.u32	Data_Dst	// address 
	.u32	TO		// TimeOut:loops
.ends
.assign DAQ_Config, r10, r13, DAQConf

.macro  NOP32
		NOP
		NOP
		NOP
.endm

/////////////////////////////////////////
// 		CONSTANTS 	/////////
/////////////////////////////////////////
// ADC Data Pins
#define DB0     8   // P8-27  //ONLY PRU1
#define DB1     10  // P8-28  //ONLY PRU1
#define DB2     9   // P8-29  //ONLY PRU1
#define DB3     6   // P8-39  //ONLY PRU1
#define DB4     7   // P8-40  //ONLY PRU1
#define DB5     4   // P8-41  //ONLY PRU1
#define DB6     5   // P8-42  //ONLY PRU1
#define DB7     2   // P8-43  //ONLY PRU1
#define DB8     3   // P8-44  //ONLY PRU1
#define DB9     0   // P8-45  //ONLY PRU1
#define DB10    1   // P8-46  //ONLY PRU1
#define DB11	16  // P9-26  //ONLY PRU1

// ADC Outputs
#define bCONVST	15 // P8-11
#define bWR		14 // P8-12

// ADC Inputs
#define BUSY	15 // P8-15




//Volatile PRU mem space = (0x0000)
#define SHAREDh			0x0000
//HOST (Python) Memory space = (0x0000)_python, (0x0000)_PRU0, (0x2000)_PRU1
#define HOST_DDR_ADDRh	0x0004
#define HOST_SLh		0x0008	// sample length
#define HOST_SRh		0x000C
//PRU Personal Space = (0x0000)_PRUx
#define PRU_STATEh		0x0012


/////////////////////////////////////////
// 		MACROS 	/////////
/////////////////////////////////////////

.macro	Sub_Sample_Controller 
.mparam LABEL
		QBEQ RELOAD, DQ.Sub_Sample, 1
          MOV DQ.Sub_Sample, 1 				//bit must be zero. setting it to 1 .
          QBA LABEL
		RELOAD:
		MOV DQ.Sub_Sample, 0 				//bit must be 1. Set it to 0
.endm