/*
 * Hydrophone.h
 *
 *  Created on: Nov 4, 2014
 *      Author: Josh
 */

#ifndef HYDROPHONE_H_
#define HYDROPHONE_H_

/* INFO: This bit of a lib simply act like a specialized ADC
 * Library. The hydrophone has no computing power it self, but
 * still, it might be nice to abstract all the control that the
 * ADC must use inorder to interface with it.
 */

/* RULES FOR THE ROAD
 *   1) VCC-0.3 < AVCC < VCC+.3
 */

#define Hydrophone_DDR 		DDRC
#define Hydrophone_PORT 	PORTC
#define Hydrophone_PIN 		0
#define Hydrophone_Mask 	1<<Hydrophone_PIN



// function prototype
void ADC_Init();
void Hydrophone_Init();
int *CollectHydrophoneData(int *buf, int size);
void Timer0_Init();


#endif /* HYDROPHONE_H_ */
