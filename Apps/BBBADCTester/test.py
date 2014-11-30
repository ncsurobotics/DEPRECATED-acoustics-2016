import BBBIO

# settings
scope = 'FULL'	
DB_pin_table = ['P8_03','P8_04','P8_05','P8_06','P8_07','P8_08','P8_09','P8_10','P8_11','P8_12','P8_13','P8_14']
WR_pin = 62
BUSY_pin = 37
CS_pin = 36


# program
if scope == 'FULL':
	DB_pin_table = DB_pin_table
elif scope == 'SMALL':
	DB_pin_table = DB_pin_table[0:2]
else:
	DB_pin_table = ""

PortDB = BBBIO.Port()
PortDB.createPort(DB_pin_table)
