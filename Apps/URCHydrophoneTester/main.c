/*
 * main.c
 *
 *  Created on: Nov 4, 2014
 *      Author: Josh
 */

#include <avr/io.h>
#include <util/delay.h>
#include "Hydrophone.h"
#include "SerialApp.h"


void AVR_Init()
{
	// Setup AVR Registers
}

int main()
{
	//AVR_Init();
	Hydrophone_Init();
	Serial_Init();

	unsigned int PACKET_SIZE = 2;

	int *DataForPython;
	int buf[512] = {0};

	while(1)
	{
		WaitForPermissionForData(PACKET_SIZE); // writes W and int to python
		LED_PORT |= 1<<LED_PIN;
		DataForPython = CollectHydrophoneData(buf,PACKET_SIZE);
		LED_PORT &= ~1<<LED_PIN;
		SendForProcessing(DataForPython,PACKET_SIZE);
	}

	return 0;
}
