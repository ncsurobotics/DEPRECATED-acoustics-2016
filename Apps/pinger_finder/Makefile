COMPILER=pasm -b
FILENAME0=init0
FILENAME1=init1
FILENAME2=ADS7865_sample
FILENAME3=pru1

.PHONY: clean all

all:
	$(COMPILER) $(FILENAME0).p
	$(COMPILER) $(FILENAME1).p
	$(COMPILER) $(FILENAME2).p
	$(COMPILER) $(FILENAME3).p


clean:
	rm -rf $(FILENAME0).bin
	rm -rf $(FILENAME1).bin
	rm -rf $(FILENAME2).bin
	rm -rf $(FILENAME3).bin
