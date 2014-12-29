COMPILER=pasm -b
FILENAME1=ADS7865_sample
FILENAME2=pru1

.PHONY: clean all

all:
	$(COMPILER) $(FILENAME1).p
	$(COMPILER) $(FILENAME2).p


clean:
	rm -rf $(FILENAME1).bin
	rm -rf $(FILENAME2).bin
