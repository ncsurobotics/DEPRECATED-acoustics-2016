# some_file.py
import sys
sys.path.insert(0, '../pinger_finder')

import boot

def enable_uart():
	boot.uart()

def disable_uart():
	boot.nouart()
