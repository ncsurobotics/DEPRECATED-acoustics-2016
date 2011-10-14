    .arch msp430f2112
    .cpu 430
    .mpy none

    .section .init9,"ax",@progbits
    .p2align 1,0
    .global main
    .type main,@function

/* This code runs on the MSP430 and is responsible for generating the
   CONVST signals for the ADCs, clocking the PPI interface, and
   arbitrating the parallel bus to send sample data to the DSP */

main:
    /* Disable watchdog */
    mov #0x5a80, &__WDTCTL

    /* Configure clock */
    mov.b #0x60, &__DCOCTL
    bis.b #0x0f, &__BCSCTL1

    /* Set all pins as outputs and zero them all initially */
    mov.b #0xff, &__P1DIR
    mov.b #0x00, &__P1OUT
    mov.b #0x00, &__P1REN
    mov.b #0x00, &__P1SEL

    /* Put all steps into registers first to save cycles
          P1.0 - !CS ADC0 
          P1.1 - !CS ADC1
          P1.2 - A/!B 
          P1.3 - Frame sync
          P1.4 - !CONVST 
    */
    mov.b #0b11110, r15 
    mov.b #0b10110, r14
    mov.b #0b11101, r13
    mov.b #0b00101, r12
    mov.b #0b01010, r11
    mov.b #0b10010, r10
    mov.b #0b11001, r9
    mov.b #0b10001, r8

    /* Delay count in cycles. Lower two bits will be cleared (multiple of 4) */
    mov #28, r7
    bic #0b11, r7

    /* Overall conversion rate is 15.25 Mhz / (r7 + 35 + 1 + 2) = 242.1 Ksps
        NOTE: Actual is 238.6
     */
.L1:
    /* Run pattern (8 * 4 = 32 cycles) */
    mov.b r15, &__P1OUT 
    mov.b r14, &__P1OUT
    mov.b r13, &__P1OUT
    mov.b r12, &__P1OUT
    mov.b r11, &__P1OUT
    mov.b r10, &__P1OUT
    mov.b r9,  &__P1OUT
    mov.b r8,  &__P1OUT

    /* Delay (r7 + 1 cycles) */
    mov r7, r6
.L2:
    decd r6
    decd r6
    jnz .L2

    /* Loop (2 cycles) */
    jmp .L1
