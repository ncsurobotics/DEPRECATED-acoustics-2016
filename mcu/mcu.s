    .arch msp430f2112
    .cpu 430
    .mpy none
    .global main

#include "msp430.h"

/* This code runs on the MSP430 and is responsible for generating the
   CONVST signals for the ADCs, clocking the PPI interface, and
   arbitrating the parallel bus to send sample data to the DSP */

main:
    /* Disable watchdog */
    mov #0x5a80, &WDTCTL

    /* Configure clock */
    bic.w #OSCOFF, r2          ; Enable oscillator
    bis.b #XTS, &BCSCTL1       ; Set high-frequency oscillator mode
    mov.b #LFXT1S_2, &BCSCTL3  ; Oscillator frequency 3-16Mhz
.L1:
    bic.b #OFIFG, &IFG1        ; Clear oscillator fault flag
    mov.w #0xff, r15           ; Delay
.L2:
    dec.w r15
    jnz .L2
    bit.b #OFIFG, &IFG1        ; Check interrupt fault flag
    jnz .L1
    bis.b #SELM_3, &BCSCTL2    ; Switch MCLK to LXFT1


    /* Set all pins as outputs and zero them all initially */
    mov.b #0xff, &P1DIR
    mov.b #0x00, &P1OUT
    mov.b #0x00, &P1REN
    mov.b #0x00, &P1SEL

    /* Put all steps into registers first to save cycles
          P1.0 - !CS ADC0 
          P1.1 - !CS ADC1
          P1.2 - A/!B 
          P1.3 - Frame sync
          P1.4 - !CONVST
          P1.5 - PPICLK
    */
    mov.b #0b010001, r15 
    mov.b #0b101110, r14
    mov.b #0b001110, r13
    mov.b #0b110010, r12
    mov.b #0b010010, r11
    mov.b #0b110101, r10
    mov.b #0b010101, r9
    mov.b #0b110001, r8

    /* Delay count in cycles. Lower two bits will be cleared (multiple of 4) */
    mov #44, r7
    bic #0b11, r7

    /* Overall conversion rate is 16 Mhz / (32 + r7 + 1 + 2) = 202.5 Ksps
    
       Note: mov from register to memory is 4 cycles, mov from register to 
       register is 1 cycle, decd is 1 cycle, and all jumps require 2 cycles
     */
.L3:
    /* Run pattern (8 instructions * 4 cycles/instruction = 32 cycles) */
    mov.b r15, &P1OUT 
    mov.b r14, &P1OUT
    mov.b r13, &P1OUT
    mov.b r12, &P1OUT
    mov.b r11, &P1OUT
    mov.b r10, &P1OUT
    mov.b r9,  &P1OUT
    mov.b r8,  &P1OUT

    /* Delay (r7 + 1 cycles) */
    mov r7, r6
.L4:
    decd r6
    decd r6
    jnz .L4

    /* Loop (2 cycles) */
    jmp .L3
