
mcu.bin: mcu.s
	msp430-gcc -D_GNU_ASSEMBLER_ -x assembler-with-cpp -mmcu=msp430f2112 -o $@ $<

clean:
	rm mcu.bin

.PHONY: clean
