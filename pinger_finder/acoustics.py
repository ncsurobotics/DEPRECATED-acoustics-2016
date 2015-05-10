from sys import argv

from bbb.ADC import ADS7865
from bbb.LTC1564 import LTC1564
import locate_pinger

class Acoustics():
    def __init__(self):
        self.adc = ADS7865()
        self.filt = LTC1564()
        
    def preset(self,sel):
        if sel==0:
            self.adc.preset(0)
            self.filt.gain_mode(0)
            
        elif sel==100:
            self.adc.preset(100)
            self.filt.gain_mode(15)
            
    def compute_pinger_direction(self):
        val = locate_pinger.main(self.adc, dearm=False)
        return val
        
    def close(self):
        self.adc.unready()