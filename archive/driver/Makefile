obj-m := ppiadc.o

KERNEL_SRC ?= ../../uclinux-dist/linux-kernel
CFLAGS_MODULE = -I$(PWD)/../include/

all:
	make -C $(KERNEL_SRC) SUBDIRS=$(PWD) modules

clean:
	make -C $(KERNEL_SRC) SUBDIRS=$(PWD) clean

.PHONY: all clean
