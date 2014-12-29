// timer_app.p: Works with a python script in order to measure
// the amount of time that it takes to exit the ROADBLOCK loop.
// currently, r0 (the counter) is set to 0xBEBC200, corresponding
// to 200*(10)^6 clock cycles. That means every second of time taken
// to complete the loop is attributed to 1 clk cycle of execution
// time.

.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

        MOV  r0, 0xBEBC200
        MOV  r2, 0
ROADBLOCK:
        QBEQ END, r0, 0
        SUB  r0, r0, 1
//        LBBO r1, r2, 0, 4
        QBA  ROADBLOCK
        //QBEQ ROADBLOCK, r1, 1
END:
        MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        HALT
