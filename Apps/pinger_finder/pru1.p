.origin 0
.entrypoint START

#define DB0     8   // P8-27
#define DB1     10  // P8-28
#define DB2     9   // P8-29
#define DB3     6   // P8-39
#define DB4     7   // P8-40
#define DB5     4   // P8-41
#define DB6     5   // P8-42
#define DB7     2   // P8-43
#define DB8     3   // P8-44
#define DB9     0   // P8-45
#define DB10    1   // P8-46

// r1: Data to put in DRAM[0]
// r2: Ptr to DRAM[0]

START:
        LBCO r0, C4, 4, 4       // Load Bytes Constant Offset (?)
        CLR  r0, r0, 4          // Clear bit 4 in reg 0
        SBCO r0, C4, 4, 4       // Store Bytes Constant Offset

        //MOV  r1, 1              // Setup bit be pru1 ack bit
        //MOV  r2, 0x0000         // address to DRAM1[0]
        //SBBO r1, r2, 0, 4       // Store data in DRAM1[0]
END:
        HALT
