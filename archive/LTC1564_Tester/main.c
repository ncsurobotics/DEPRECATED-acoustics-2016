/*
 * main.c
 *
 *  Created on: Oct 25, 2014
 *      Author: Josh
 */
#define F_CPU 16000000UL

#include <stdlib.h>
#include <avr/io.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include "lcd.h"
#include "LTC1564.h"

/* Set ports:
 * The following ports are already taken by the lcd lib:
 * 		PortD[0:6] -- LCD data and control lines
 *
 * The following ports are already taken by the LTC1564
 * 		PortB[0:3] -- F register control lines.
 * 		PortC[0:3] -- G register control lines.
 *
 */


void Init_Avr()
{
	// Do nothing
}

void main()
{
	// Initialize AVR
	Init_Avr();

	// Initialize LCD
	lcd_init(LCD_DISP_ON);
	lcd_clrscr();
	lcd_puts("LTC1564");

	// Initialize LTC1564
	LTC1564_init();

	LTC1564_send(1,3);

	for(DDRD |= 1<<7;;){
		PORTD ^= 1<<7; // Blink LED
		_delay_ms(1000);
	}

}
