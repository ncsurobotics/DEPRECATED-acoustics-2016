
mcu.bin: mcu.s
	msp430-gcc -mmcu=msp430f2112 -o $@ $<

clean:
	rm mcu.bin

.PHONY: clean
