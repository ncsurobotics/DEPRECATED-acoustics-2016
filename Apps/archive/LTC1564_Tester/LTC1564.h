/*
 * LTC1564.h
 *
 *  Created on: Oct 25, 2014
 *      Author: Josh
 */

#ifndef LTC1564_H_
#define LTC1564_H_

/* SET MACROS */
#define LTC1564_f_port 	PORTB
#define LTC1564_f_DDR 	DDRB
#define LTC1564_f_pin 	PINB
#define f0 				0
#define f1 				1
#define f2				2
#define f3				3
#define LTC1564_f_portMask 		(1<<f0 | 1<<f1 | 1<<f2 | 1<<f3)

#define LTC1564_g_port 	PORTC
#define LTC1564_g_DDR 	DDRC
#define LTC1564_g_pin 	PINC
#define g0 				0
#define g1				1
#define g2				2
#define g3				3
#define LTC1564_g_portMask 		(1<<g0 | 1<<g1 | 1<<g2 | 1<<g3)

#define LTC1564_csBar_port 	PORTC
#define LTC1564_csBar_DDR 	DDRC
#define LTC1564_csBar 	4
#define LTC1564_csBar_portMask 	1<<LTC1564_csBar

/* Prototype functions */
void LTC1564_init();
void LTC1564_send(int g, int f);

#endif /* LTC1564_H_ */
