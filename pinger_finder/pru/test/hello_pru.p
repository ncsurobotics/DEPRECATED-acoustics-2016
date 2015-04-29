.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

END:
        MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        HALT
