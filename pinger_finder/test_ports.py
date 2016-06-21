from bbb import port
from time import sleep

value = 1
pins = ['P9_25','P8_46','P8_45','P8_44','P8_43','P8_42','P8_41','P8_40','P8_39','P8_30','P8_29','P8_28','P8_27','P9_26','P9_27','P9_28','P9_29','P9_30','P9_31']

test = port.Port()
test.create_port(pins)
test.set_port_dir('out')
while 1:
    if value==1:
        test.write_to_port(0b1111111111111111111)
        value = 0
    elif value == 0:
        test.write_to_port(0)
        value = 1

    sleep(.2)
