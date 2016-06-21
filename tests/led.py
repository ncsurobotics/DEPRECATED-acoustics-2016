import os

USR0 = '/sys/class/leds/beaglebone\:green\:usr0/'

class USR0_LED:
    def __init__(self):
        self.free()
    
    def free(self):
        os.system('echo none > ' + USR0 + 'trigger')
    def reset(self):
        os.system('echo heartbeat > ' + USR0 + 'trigger')
    def brightness(self,val):
        s = str(val)
        os.system('echo ' + s + ' > ' + USR0 + 'brightness')

