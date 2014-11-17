/*
 * SerialApp.h
 *
 *  Created on: Nov 4, 2014
 *      Author: Josh
 */

#ifndef SERIALAPP_H_
#define SERIALAPP_H_

#define TX_PORT PORTD
#define TX_DDR DDRD
#define TX_PIN 1

#define LED_PORT PORTB
#define LED_DDR DDRB
#define LED_PIN 1

void Serial_Init();
void serialPutc(unsigned char DataOut);
void serialPuts(unsigned char *DataOut);
unsigned char serialRead(void);
void WaitForPermissionForData(unsigned int size);
void SendForProcessing(int *data, unsigned int size);

#endif /* SERIALAPP_H_ */
