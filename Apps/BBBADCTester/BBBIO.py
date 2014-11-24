import os

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
