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
#define TO_EN

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
#define Col_Act 2
.struct DAQ_State
	.u32	Sample
	.u16	TapeHD_Offset
	.u8	PRU0_State
	.u8	PRU1_State
	.u8	PRU0_State_Ptr
	.u8	PRU1_State_Ptr
.ends
.assign DAQ_State, r5, r7.w0, DAQState


.struct DAQ_Config
	.u32	Samp_Len	// samples
	.u32	Samp_Rate	// loops
	.u32	Data_Dst	// address 
	.u32	TO		// TimeOut:loops
.ends
.assign DAQ_Config, r8, r11, DAQConf

/////////////////////////////////////////
// 		CONSTANTS 	/////////
/////////////////////////////////////////
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
