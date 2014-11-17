/*
 * Hydrophone.c
 *
 *  Created on: Nov 4, 2014
 *      Author: Josh
 */

#include <string.h>
#include <avr/io.h>
#include "Hydrophone.h"
#include <avr/interrupt.h>
#include "SerialApp.h"

volatile int n;
volatile int out[500] = {0};


int *CollectHydrophoneData(int *buf, int size)
{
	// initalize some variables
	ADCSRA |= 1<<ADIF; //a logical one clears this interuppt flag.
	TIFR0 |= (1<<OCF0A);
	n = 0;

	// enable interrupt functionality
	sei();
	ADCSRA |= (0<<ADSC | 1<<ADIE | 1<<ADATE);

	// hang inside a while loop untill ADC capture is finished
	//LED_PORT |= 1<<LED_PIN; LED_PORT &= ~(1<<LED_PIN);
	while(n<size) {}

	// Disable interupt functionality
	ADC &= ~1<<ADIE;
	cli();

	// Copy captured data to a register and return
	for(int i = 0; i < size; i++) {
		buf[i] = out[i];
	}

	return buf;
}





ISR(ADC_vect)
{
	out[n] = ADCH;
	n++;

	/* The ADC is triggered by the output compare register flag (OCF0A). OCF0A gets
	 * set every time timer0 hits the compare match threshold set back in the
	 * "Timer0_Init()" function, but it won't clear unless it's ISR occurs. Timer0's ISR
	 *  never occurs because this code uses the ADC's ISR instead. Since OCF0A is the
	 *  ADC's source of automated triggering, the ADC will IGNORE all conversion start
	 *  commands until the OCF0A is cleared. Hence is why there is a command to
	 *  clear OCF0A below.
	 */
	TIFR0 |= (1<<OCF0A);
}


/* ************** LEVEL 2 ****************** */

void Hydrophone_Init()
{
	ADC_Init();
	Timer0_Init();
}

/* ************** LEVEL 1 ****************** */

void ADC_Init()
{
	//DIDR0 = 0x3E; //Leave only ADC0 active
	ADMUX = 0x60; //AVcc Reference, Left Adjusted, ADC0 Selected
	ADCSRB |= 0x03; //ADTS = 3;
	ADCSRA = 1<<ADEN | 4<<ADPS0; //Enable ADC, 16TimesPrecaler
}

void Timer0_Init()
{
	TCCR0A = 0x02; //Set part WGM for CTC mode
	TCCR0B = 0x05; // Set other part of WGM and PRESCALER = 1024
	OCR0A = 0x7F; // Select the Comparison point
}
