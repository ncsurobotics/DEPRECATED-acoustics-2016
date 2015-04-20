COMPILER=pasm -b
FILENAME0=init0
FILENAME1=init1
FILENAME2=ADS7865_sample
FILENAME3=pru1

.PHONY: clean all

all:
	$(COMPILER) $(FILENAME0).p -b bin/$(FILENAME0)
	$(COMPILER) $(FILENAME1).p -b bin/$(FILENAME1)
	$(COMPILER) $(FILENAME2).p -b bin/$(FILENAME2)
	$(COMPILER) $(FILENAME3).p -b bin/$(FILENAME3)


clean:
	rm bin/$(FILENAME0).bin
	rm bin/$(FILENAME1).bin
	rm bin/$(FILENAME2).bin
	rm bin/$(FILENAME3).bin
	rm *.pyc
