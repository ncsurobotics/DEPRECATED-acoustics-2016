.origin 0
.entrypoint START

#define PRU0_ARM_INTERRUPT 19

// r0: Timeout counter
// r1: Advance bit coming from PRU1
// r2: Ptr to DRAM[0]

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

        MOV  r0, 0xBEBC200      // Ready up the timout counter
        MOV  r2, 0x2000         // R2 points to DRAM1[0]
       
ROADBLOCK:
        QBEQ END, r0, 0         // Check Timeout ctr. End program if too long.
        SUB  r0, r0, 1          // decrement timer.
        LBBO r1, r2, 0, 4       // Grab data from DRAM1[0]
        QBEQ ROADBLOCK, r1, 0   // Loop as long as PRU1 didnt intervene

END:
        MOV r31.b0, PRU0_ARM_INTERRUPT+16 // Send notification to host for program completion
        HALT
