#include "prustdlib.h"
#include "pingerFinderLib.h"

//-----------------------------------------------
//---------------- FUNCTIONS ------------------
//-----------------------------------------------

.macro  Wait_For_COLL_CLR_Signal
.mparam LABEL
        LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)
        QBBS LABEL, DQ.PRU0_State, COLL
.endm
    
.macro  Conf_DataDst_For_DDR_Address
        LBBO DAQConf.Data_Dst, DQ.PRU0_Ptr, HOST_DDR_ADDRh, 4 
.endm

.macro  Get_SL_From_Host
        LBBO DAQConf.Samp_Len, DQ.PRU0_Ptr, HOST_SLh, 4
        ADD DAQConf.Samp_Len, DAQConf.Samp_Len, 4 // Add one extra block for status bit
.endm 

.macro  Set_COLL_High_On_PRU0
    LBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
    SET  DQ.PRU0_State, COLL    // vvv
    SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State) 
                                // Share PRU State
                                // ^ state: collecting
.endm


.macro Get_Absolute_Value
.mparam R
        QBBC    RET_ABS, R, 11
          SUB   R, R, 1
          OR    R, R, GP.Extension
          NOT   R, R
        
        RET_ABS:
.endm

.macro  Init_Threshold_Value
        LBBO DAQConf.Trg_Threshold, DQ.PRU0_Ptr, HOST_THRh, 4
.endm

.macro Super_Sample_Counter
    QBGT SUPSAMP_ADD, DQ.Super_Sample, 3
      MOV  DQ.Super_Sample, 0
      QBA  SUPSAMP_RET
    SUPSAMP_ADD:
    ADD  DQ.Super_Sample, DQ.Super_Sample, 1

    SUPSAMP_RET:
.endm

.macro Init_PRU0_Timer
    // enable the counter
    LBBO GP.Cpr, DQ.PRU0CTRL, pru_CTRL, 4
    SET  GP.Cpr, pru_CTR_EN_bit
    SBBO GP.Cpr, DQ.PRU0CTRL, pru_CTRL, 4
    
    // Init counter to zero
    MOV  GP.Cpr, 0
    SBBO GP.Cpr, DQ.PRU0CTRL, pru_CYCLE, 4
.endm

.macro Send_Status_Data
    SBBO DQ.Sample_Ctrl, DAQConf.Data_Dst, DQ.TapeHD_Offset, SIZE(DQ.Sample_Ctrl) // submit data to DDR
    INCR DQ.TapeHD_Offset, 4 // increment pointer
.endm

.macro Init_Db_Register
    LBBO DAQConf.DB_LIMIT, DQ.PRU0_Ptr, HOST_DBh, SIZE(DAQConf.DB_LIMIT)
.endm
    
.macro Incr_Deadband
.mparam incr_val
    ADD DQ.Deadband_CNTR, DQ.Deadband_CNTR, incr_val
    QBGT  EXIT_INCR_DEADBAND, DQ.Deadband_CNTR, DAQConf.DB_LIMIT
      SET DQ.Sample_Ctrl, DBOVF
EXIT_INCR_DEADBAND:
.endm

.macro Flag_Trigger_Channel
     QBBC EXIT_Flag_Trigger_Channel0, DQ.Super_Sample, 0
        // The sub sample is 1. we are either looking at
        // channel 1, or channel 3.
        SET  DQ.Sample_Ctrl, TFLG0
     
     EXIT_Flag_Trigger_Channel0:
     QBBC EXIT_Flag_Trigger_Channel1, DQ.Super_Sample, 1
        // the super sample is 1. We are looking at channels
        // 2 and 3 (depending on what the sub sample is).
        SET  DQ.Sample_Ctrl, TFLG1
     
     EXIT_Flag_Trigger_Channel1:
.endm
    

//-----------------------------------------------
//--------------- MAIN PROGRAM ------------------
//-----------------------------------------------

.origin 0
.entrypoint START

START:
    LBCO r0, CONST_PRUCFG, 4, 4   // Load SYSCFG register to r0
    CLR  r0, r0, 4                // Essentially clears SYSCFG["OCP_ACTIVELOW"] 
    SBCO r0, CONST_PRUCFG, 4, 4   // Writes change to SYSCFG register


PREPARE:
    MOV DQ.Sample_Ctrl, 0           // Init Sample Ctrl Register
    MOV DQ.Deadband_CNTR, 0         // Init Deadband Counter
    Init_Db_Register
    
    LDI  DQ.PRU0_Ptr, 0x0000        // Init PRU0 ptr
    LDI  DQ.PRU1_Ptr, 0x2000        // Init PRU1 ptr
    
    MOV  DQ.PRU0_State, 0           // Init status register
    SBBO DQ.PRU0_State, DQ.PRU0_Ptr, PRU_STATEh, SIZE(DQ.PRU0_State)

    Conf_DataDst_For_DDR_Address    // Data will go to DDRAM.
    Get_SL_From_Host                // Receive SL from HOST.
    MOV  DQ.Sub_Sample, 0           // Known that first sample is sub_sample 0
    MOV  DQ.Super_Sample, 0         // Known that first sample is super_sample 0
    //MOV  DAQConf.Samp_Len, 35     // Set sample length to 10  
    
    MOV GP.Extension, 0xFFFFF000        // Negative sign extension register
    MOV DAQConf.Trg_Threshold, 0x0002   // For the Trigger logic
    
    Init_Threshold_Value                // load
    
    MOV  DQ.PRU0CTRL, PRUCTRL_BASE_ADDR // init ptr to PRUCTRL
    MOV  DAQConf.TO, DEFAULT_TO_TIME    // init TO value to DEFAULT
    Init_PRU0_Timer                     // Start and init TO timer to 0 cycles

    // SET Default outputs
    SET  r30, bCONVST
    
//-----------------------------------------------
//--------------- SAMPLING BLOCK ------------------
//-----------------------------------------------

TOP:
    // DQ.TapeHD_Offset: a variable representing the current position/offset of
    // the pointer writing to DDRAM. Once DQ.TapeHD_Offset > DAQConf.Samp_Len,
    // we know that we have collected all the samples that the user has requested,
    // and the program will end. 
    //   NOTE: DQ.TapeHD_Offset must increment in steps of 4, as DDRAM is only 32 bit
    //   addressable.
    
    // DAQConf.Samp_Len: Variable that represents "4*n_samples_requested".
    /////
    
    QBLT END, DQ.TapeHD_Offset, DAQConf.Samp_Len

    #ifdef TO_EN
    QBEQ END, DAQConf.TO, 0     // Check Timeout ctr. End program if too long.  
     DECR DAQConf.TO, 1         // decrement timer.
    #endif


TRIG:
    // PRU has determined that it has not yet fulfilled its sample qouta, thus
    // it will wait for the other pru to raise CINT, thus signaling that enough
    // time has elapsed to go ahead and collected another sample. 
    
    LBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)
    QBBC TRIG, DQ.PRU1_State, CINT  
    // ^^ Advance only when other PRU signals a new conversion!
    
    CLR  DQ.PRU1_State, CINT // re-init CINT for next time
    SBBO DQ.PRU1_State, DQ.PRU1_Ptr, PRU_STATEh, SIZE(DQ.PRU1_State)

CONVST: 
    CLR  r30, bCONVST               // Trigger a Conversion on ADC

WAIT:
    // connect bCONVST to BUSY pin in order to bypass this portion
    NOP32;  // delay just in case
    NOP32;
    NOP32;
    NOP32;
    NOP32;
    NOP32;
    NOP32;
    NOP32;
    SET  r30, bCONVST   // CONVST is no longer needed TAG=cleanup
    WBC  r31, BUSY      // Watch for conversion to complete
    
    // At this point, PRU0 has detected BUSY go low. Thus, a conversion
    // has been completed, and a data point is ready for collection.
    // PRU0 will now pull WR low in order to get the ADC output to 
    // output the 12-bit sample. Then it will set it's
    // COLL=1 in the PRU0 status code, which should notify PRU1 that
    // it should join in on the sample collection process.

COLLECT:
    CLR  r30, bRD       // Activate bWR
    Set_COLL_High_On_PRU0   // << Used to signal PRU1 to sample ADC

ASK_PRU1:
    Wait_For_COLL_CLR_Signal    ASK_PRU1       // << Wait for PRU1 to finish sampling.
    LBBO GP.Cpr, DQ.PRU0_Ptr, SHAREDh, 4       // << Collect PRU1s partial sample.
    SET  r30, bRD

    // At this point, PRU1s measurement has been received, and PRU0
    // has done the necessary cleanup (DR:=0, bWR:=1, COLL:=0(By PRU1). 
    // Now, PRU0 will parse the collected sample and convert it to an 
    // intelligible format.
    
    MOV  DQ.Sample, 0       // re-init the sample reg
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
    QBBC PROCESS, GP.Cpr, DB0
     SET DQ.Sample, 0


//-----------------------------------------------
//------------ PROCESSING BLOCK ----------------
//-----------------------------------------------


PROCESS:
    QBBS  SUBMIT,DQ.Sample_Ctrl, TRGD
      // At this point, the TRGD bit is not set yet. Thus, we'll perform
      // some analysis to see if the threshold has been surpassed on this 
      // particular sample. If not, then we'll jump to the next state block
      // without writing the sample to memory.
      MOV  DQ.Sample_Abs, DQ.Sample     
      Get_Absolute_Value  DQ.Sample_Abs
      QBLT INCR_DEADBAND, DAQConf.Trg_Threshold, DQ.Sample_Abs
      // The threshold has been surpassed. Next step will be to check if 
      // the deadband limit has been surpassed.  
      
      // v One can alter the DEFAULT_DEADBAND_TRG_LIMIT by changing
      // v the define statement in pingerFinderLib.h. It should be safe
      // v to set that parameter to zero if one wishes to disable the
      // v deadband trigger
      Incr_Deadband 0
      QBBC ZERO_DEADBAND, DQ.Sample_Ctrl, DBOVF
        // The deadband limit has been exceeded, this alongside the fact that
        // the triggering threshold was also surpassed means that the program
        // will set TRGD=1.
        SET  DQ.Sample_Ctrl, TRGD
        
        // While trigger is being set, some bits indicating which channel the
        // trigger occurred on will also be set
        Flag_Trigger_Channel
        
        // Commence sending data to the user
        Send_Status_Data
        QBA SUBMIT

        
    ZERO_DEADBAND:
        MOV DQ.Deadband_CNTR, 0
        QBA TIMEOUT_CTRL
        
    INCR_DEADBAND:
        Incr_Deadband 1
        QBA TIMEOUT_CTRL
        
        
TIMEOUT_CTRL:
    LBBO DAQConf.t, DQ.PRU0CTRL, pru_CYCLE, 4
    QBGT CONTROLLER, DAQConf.t, DAQConf.TO // Skip to NEXT_STATE if (TO > t)
      // The watchdog timer has expired. Time to undo the trigger hold, alert
      // the user, and collect whatever data is available at the moment.
      SET  DQ.Sample_Ctrl, TRGD
      SET  DQ.Sample_Ctrl, TOF
      Send_Status_Data
      QBA  CONTROLLER


SUBMIT:
    QBBC ARMING_CTRL, DQ.Sample_Ctrl, ARMD
      SBBO DQ.Sample, DAQConf.Data_Dst, DQ.TapeHD_Offset, SIZE(DQ.Sample) // submit data to DDR
      INCR DQ.TapeHD_Offset, 4 // increment pointer
      QBA CONTROLLER

ARMING_CTRL:
    QBNE CONTROLLER, DQ.Super_Sample, 0
      SET DQ.Sample_Ctrl, ARMD
      QBA SUBMIT
      
//-----------------------------------------------
//------------ NEXT STATE BLOCK ----------------
//-----------------------------------------------

CONTROLLER:
    Super_Sample_Counter
    Sub_Sample_Controller WAIT
        // Sub_Sample_Controller will either make a shortcut to the CONVST
        // step, or go all the way back at the top of the cycle... depending
        // on the sub_sample that was just collected.
    
    QBA  TOP// loop back to Top Branch instruction
    
//-----------------------------------------------
//------------ EPILOGUE BLOCK ----------------
//-----------------------------------------------
    
END:
    MOV  GP.Cpr, 0
    SBBO GP.Cpr, DAQConf.Data_Dst, DQ.TapeHD_Offset, SIZE(DQ.Sample) // submit data to DDR
    SET  r30, bCONVST
    MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        MOV DQ.TapeHD_Offset, 0 // Clear the offset as preparation for next run
    HALT
