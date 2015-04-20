/*
 * LTC1564.c
 *
 *  Created on: Oct 25, 2014
 *      Author: Josh
 */


#include <stdlib.h>
#include <avr/io.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include "LTC1564.h"

void LTC1564_init()
{
	// Set Outputs to interface with the LTC
	LTC1564_f_DDR |= LTC1564_f_portMask;
	LTC1564_g_DDR |= LTC1564_g_portMask;
	LTC1564_csBar_port |= 1<<LTC1564_csBar;
	LTC1564_csBar_DDR |= LTC1564_csBar_portMask;

}

void LTC1564_send(int g, int f)
{
	// Inititalize vars
	int d[8] = {0};
	int i;
	int bSave = PINB;
	int cSave = PINC;


	// prepare g for output
	for(i = 0 ; g > 0;)
	{
		d[i] = g%2;
		i++;
		g = g/2;
	}

	// output the g registers
	LTC1564_g_port = (LTC1564_g_pin & ~LTC1564_g_portMask) | (d[0]<<g0 | d[1]<<g1 | d[2]<<g2 | d[3]<<g3);


	// prepare f for output
	for(i = 0; f > 0;)
	{
		d[i] = f%2;
		i++;
		f = f/2;
	}

	// output the f registers
	LTC1564_f_port = (LTC1564_f_pin & ~LTC1564_f_portMask) | (d[0]<<f0 | d[1]<<f1 | d[2]<<f2 | d[3]<<f3);


	// set cf low for 1ms
	LTC1564_csBar_port &= ~(1<<LTC1564_csBar);
	_delay_ms(1);

	// set the cf high
	LTC1564_csBar_port |= 1<<LTC1564_csBar;

	// return registers back to their previous state
	PORTB = bSave;
	PORTC = cSave;
}
