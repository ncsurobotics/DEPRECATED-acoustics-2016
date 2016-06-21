from bbb import port
from time import sleep

def test1(array):
    while 1:
        for pin in array.pins:
            pin.write(1)
            sleep(0.1)
            pin.write(0)

def test2(array):
    while 1:
        for i in range(2**8 - 1):
            print(i)
            array.write_to_port(i)
            sleep(0.1)

value = 1
pins = ['P9_11','P9_12','P9_13','P9_14','P9_15','P9_16','P9_17','P9_18']

test = port.Port()
test.create_port(pins)
test.set_port_dir('out')
test1(test)
