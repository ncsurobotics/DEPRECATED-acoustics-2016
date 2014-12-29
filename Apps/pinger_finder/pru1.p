.origin 0
.entrypoint START

// r1: Data to put in DRAM[0]
// r2: Ptr to DRAM[0]

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

        MOV  r1, 0              // Setup bit be pru1 ack bit
        MOV  r2, 0x0000         // address to DRAM1[0]
        SBBO r1, r2, 0, 4       // Store data in DRAM1[0]
END:
        HALT
