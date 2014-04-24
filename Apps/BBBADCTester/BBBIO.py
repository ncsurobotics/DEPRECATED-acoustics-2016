import os
import sys

def batchLookupGPIO(pinList):
	i = 0
	GPIOList = [None]*len(pinList)
	lookupTable = {'P8_03': 38,
		'P8_04': 39,
		'P8_05': 34,
		'P8_06': 35,
		'P8_07': 66,
		'P8_08': 67,
		'P8_09': 69,
		'P8_10': 68,
		'P8_11': 45,
		'P8_12': 44,
		'P8_13': 23,
		'P8_14': 26,
		'P8_15': 47,
		'P8_16': 46,
		'P8_17': 27,
		'P8_18': 65,
		'P8_20': 63,
		'P8_21': 62,
		'P8_22': 37,
		'P8_23': 36,
		'P8_24': 33,
		'P8_25': 32,
		'P8_26': 61,
		}		
	
	try:
		for pin in pinList:
			GPIOList[i] = lookupTable[pin]
			i += 1
	except KeyError:
		print('Uh oh. pin%s does not exist current' % pin)
		sys.exit(1)
	return GPIOList

class GPIO:
	def __init__(self,gpio_pin):
		self.gpio_pin = gpio_pin
		self.gpio_base = "/sys/class/gpio/"
		self.gpio_path = "/sys/class/gpio/gpio%d/"%gpio_pin
		
		os.system("echo %d > %sexport" % (gpio_pin,self.gpio_base))
		with open(self.gpio_path+"direction") as f:
			self.direction = f.read().rstrip("\n")
		self.read()

	def reInit(self):
		self.__init__(self.gpio_pin)

	def setDirection(self,targetState):
		if (targetState == "out") or (targetState == "in"):
			os.system("echo %s > %sdirection" % (targetState,self.gpio_path))
			with open(self.gpio_path+"direction") as f:
				self.direction = f.read().rstrip("\n")
		else:
			print("%s: %s is not a valid direction" % (self.gpio_pin,targetstate))

	def write(self,value):
		if self.direction == "out":
			os.system("echo %d > %svalue" % (value,self.gpio_path))
			self.value = value
		else: 
			print("pin%s is not an output. You cannot set it's value." % self.gpio_pin)
	
	def read(self):
		with open(self.gpio_path+"value") as f:
			self.value = int( f.read().rstrip("\n") )
		return self.value

	def help(self):
		print("You can call the following attributes: ")
		for item in self.__dict__.keys():
			print("  *.%s" % item)
		
		print("")
		print("You also have access to the following methods: ")
		for item in [method for method in dir(self) if callable(getattr(self, method))]:
			print("  *.%s()" % item)
		print("")

	def close(self):
		os.system("echo %d >%sunexport" % (self.gpio_pin,self.gpio_base)) 


class Port():
	def __init__(self, assignment=None):
		self.en = True
		self.pins = []
		self.direction = []
		self.value = []
		self.nValue = 0
		self.length = 0
		if assignment:
			self.createPort(assignment)
	
	def createPort(self, pinNameList):
		if type(pinNameList) == type(""):
			pinNameList = [pinNameList]

		GPIOList = batchLookupGPIO(pinNameList)
		for pin in GPIOList:
			print(pinNameList)
			print(GPIOList)
						
			obj_pin = GPIO(pin)
			self.pins.append(obj_pin)	#self.pins
			(self.direction).append(obj_pin.direction)	#self.direction
			(self.value).append(obj_pin.value)	#self.value

		self.length = len(self.pins)		#self.length

	def readStr(self):
		s = ""
		i = 0
		for pin in self.pins:
			a = pin.read()
			s = str(a) + s	
			self.value[i] = a
		return s

	def setPortDir(self, direction):
		i = 0
		for pin in self.pins:
			pin.setDirection(direction)
			self.direction[i] = pin.direction

	def close(self):
		for pin in self.pins:
			pin.close()

	def help(self):
		print("You can call the following attributes: ")
		for item in self.__dict__.keys():
			print("  *.%s" % item)
		
		print("")
		print("You also have access to the following methods: ")
		for item in [method for method in dir(self) if callable(getattr(self, method))]:
			print("  *.%s()" % item)
		print("")


