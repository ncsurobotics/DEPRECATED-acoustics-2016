CC = pasm
CFLAGS = -b

FILENAME0 = init0
FILENAME1 = init1
FILENAME2 = ADS7865_sample
FILENAME3 = pru1

.PHONY: clean all

all:
	$(CC) $(CFLAGS) $(FILENAME0).p -b bin/$(FILENAME0)
	$(CC) $(CFLAGS) $(FILENAME1).p -b bin/$(FILENAME1)
	$(CC) $(CFLAGS) $(FILENAME2).p -b bin/$(FILENAME2)
	$(CC) $(CFLAGS) $(FILENAME3).p -b bin/$(FILENAME3)


clean:
	rm bin/$(FILENAME0).bin
	rm bin/$(FILENAME1).bin
	rm bin/$(FILENAME2).bin
	rm bin/$(FILENAME3).bin
	rm ../*.pyc
