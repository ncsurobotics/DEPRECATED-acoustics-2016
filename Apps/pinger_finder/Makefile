COMPILER=pasm -b
FILENAME0=init
FILENAME1=ADS7865_sample
FILENAME2=pru1

.PHONY: clean all

all:
	$(COMPILER) $(FILENAME0).p
	$(COMPILER) $(FILENAME1).p
	$(COMPILER) $(FILENAME2).p


clean:
	rm -rf $(FILENAME0).bin
	rm -rf $(FILENAME1).bin
	rm -rf $(FILENAME2).bin
