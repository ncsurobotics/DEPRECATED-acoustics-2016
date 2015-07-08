import usb.core
import usb.util

#find our device 
dev = usb.core.find(idVendor=0x403, idProduct=0x6001)

# was it found?
if dev is None:
    raise ValueError('Device not found')
    
for cfg in dev:
    print(cfg.bConfigurationValue)
    print('')