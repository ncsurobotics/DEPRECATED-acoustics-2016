/**
 * \file
 * \brief PPI ADC Kernel Module
 */

/*
 * Memory scheme
 *
 * Samples from the ADC are interleaved
 *   A B C D A B C D A B C D A...
 *
 * DMA ping-pongs between two 80kB buffers. This size of this buffer is
 * determined as follows,
 *
 * 10240 samples, 2 bytes (16 bit) per sample, 4 channels
 *
 * 10240 * 2 * 4 = 80kB
 *
 * Two of these buffers are populated by the DMA engine in an alternating,
 * "ping-pong" fashion. When one buffers fills it becomes available for a client
 * application to use. Since this buffer will be overwritten, the user-space
 * application must copy the data to user-space.
 */

#include <asm/blackfin.h>
#include <asm/cacheflush.h>
#include <asm/dma.h>
#include <asm/portmux.h>
#include <asm/uaccess.h>

#include <linux/cdev.h>
#include <linux/completion.h>
#include <linux/fs.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/mm.h>
#include <linux/module.h>

#include "acoustics-common.h"

/**
 * \defgroup ppiadc PPI ADC Driver
 * \ingroup kernelspace
 * \brief Kernel module to interface with the PPI ADC
 * \{
 */

#define DRIVER_NAME "ppi_adc"

/* Major number of the device */
#define PPI_CHR_MAJOR 157

/* Number of buffers for the DMA engine to use. This should always be 2 */
#define BUFFER_COUNT 2

/* See Blackfin Hardware Reference Manual 3.2, page 7-27, "PPI Control Register"
 * 
 * Sample on falling edge of PPICLK, frame sync on rising edge, 16-bit data,
 * non-ITU 656 data with 1 external frame sync.
 */
#define PPI_MODE 0x780C

static irqreturn_t buffer_full_handler(int irq, void* data);
static int page_alloc_order(size_t size);

static ssize_t ppi_chr_read(struct file* filp, char __user* buffer, size_t count, loff_t* offset);
static ssize_t ppi_chr_write(struct file* filp, const char __user* buffer, size_t count, loff_t* offset);
static int ppi_chr_open(struct inode* i, struct file* filp);
static int ppi_chr_release(struct inode* i, struct file* filp);

static int ppi_init(void);
static int dma_init(void);
static int device_init(void);
static int __init ppi_adc_init(void);

static void ppi_close(void);
static void dma_close(void);
static void device_close(void);
static void __exit ppi_adc_close(void);

/* PPI pins to reserve */
static unsigned short ppi_pins[] = {P_PPI0_D0, P_PPI0_D1,
                                    P_PPI0_D2, P_PPI0_D3,
                                    P_PPI0_D4, P_PPI0_D5,
                                    P_PPI0_D6, P_PPI0_D7,
                                    P_PPI0_D8, P_PPI0_D9,
                                    P_PPI0_D10, P_PPI0_D11,
                                    P_PPI0_D12, P_PPI0_D13,
                                    P_PPI0_D14, P_PPI0_D15,
                                    P_PPI0_CLK, P_PPI0_FS1,
                                    0};

/* Pointer to the DMA buffer */
static unsigned long dma_buffer = 0;

/* Index of the currently filling buffer. The interrupt handler uses this to know which buffer just filled */
static unsigned short current_buffer_index = 0;
static unsigned long current_buffer_pointer = 0;

/* Buffer full completion flag */
DECLARE_COMPLETION(buffer_ready);

static struct cdev* dev = NULL;
static struct file_operations fops = {
    .read = ppi_chr_read,
    .write = ppi_chr_write,
    .open = ppi_chr_open,
    .release = ppi_chr_release
};

static irqreturn_t buffer_full_handler(int irq, void* data) {
    /* Compute the absolute address of the individual buffer */
    current_buffer_pointer = dma_buffer + (current_buffer_index * BUFFER_SIZE);

    /* Advance the buffer number */
    current_buffer_index = (current_buffer_index + 1) % BUFFER_COUNT;
    complete(&buffer_ready);

#ifdef PPIADC_DEBUG
    printk(KERN_INFO DRIVER_NAME ": 0x%08lX 0x%04X\n", current_buffer_pointer, ((unsigned short*) current_buffer_pointer)[0]);
#endif
    
    clear_dma_irqstat(CH_PPI);
    return IRQ_HANDLED;
}

/* Compute the required order of a page allocation */
static int page_alloc_order(size_t size) {
    size_t pages;
    int order;
    short extra;
    
    pages = size / PAGE_SIZE;
    if(size % PAGE_SIZE) {
        pages += 1;
    }

    extra = 0;
    order = 0;
    while(pages > 1) {
        if(pages & 1) {
            extra = 1;
        }
        pages >>= 1;
        order += 1;
    }

    return order + extra;
}

static ssize_t ppi_chr_read(struct file* filp, char __user* buffer, size_t count, loff_t* offset) {
    if(bfin_read_PPI_STATUS() != 0) {
        printk(KERN_WARNING DRIVER_NAME ": PPI error. PPI_STATUS (%d)\n", bfin_read_PPI_STATUS());
        bfin_write_PPI_STATUS(0);
    }

    if(sizeof(current_buffer_pointer) != count) {
        return -EINVAL;
    }

    /* Wait for buffer to fill and pointer to be set */
    if(wait_for_completion_interruptible(&buffer_ready)) {
        return -EINTR;
    }

    /* Check for backlog */
    if(completion_done(&buffer_ready)) {
        printk(KERN_WARNING DRIVER_NAME ": Missed data packet!\n");
    }

    /* Copy value of the pointer to the just filled buffer to the user buffer */
    if(copy_to_user(buffer, &current_buffer_pointer, count)) {
        return -EFAULT;
    }

    /* Reset the completion flag so completions don't pile up */
    INIT_COMPLETION(buffer_ready);

    return 0;
}

static ssize_t ppi_chr_write(struct file* filp, const char __user* buffer, size_t count, loff_t* offset) {
    uint8_t opcode = 0;

    if(count != 1) {
        printk(KERN_WARNING DRIVER_NAME ": Invalid size on write\n");
        return -EINVAL;
    }

    if(copy_from_user(&opcode, buffer, count)) {
        printk(KERN_WARNING DRIVER_NAME ": Could not copy from user buffer\n");
        return -EFAULT;
    }

    switch(opcode) {
    case 1:
        /* Reset the completion flag */
        INIT_COMPLETION(buffer_ready);
        break;
    default:
        printk(KERN_WARNING DRIVER_NAME ": invalid opcode %d\n", opcode);
        return -EINVAL;
    }

    return 0;
}

static int ppi_chr_open(struct inode* i, struct file* filp) {
    /* Reset global values */
    current_buffer_index = 0;
    current_buffer_pointer = 0;

    /* Enable DMA */
    enable_dma(CH_PPI);

    /* Enable PPI */
    bfin_write_PPI_CONTROL(bfin_read_PPI_CONTROL() | PORT_EN);

    return 0;
}

static int ppi_chr_release(struct inode* i, struct file* filp) {
    /* Disable PPI */
    bfin_write_PPI_CONTROL(bfin_read_PPI_CONTROL() & (~PORT_EN));

    /* Disable DMA */
    disable_dma(CH_PPI);

    return 0;
}

static int ppi_init(void) {
    /* Request peripheral pins for PPI */
    peripheral_request_list(ppi_pins, DRIVER_NAME);

    /* No delay between frame sync and read */
    bfin_write_PPI_DELAY(0);
    
    /* Read one sample per frame sync (the number given for COUNT is always one
       less than the desired count) */
    bfin_write_PPI_COUNT(3);
    bfin_write_PPI_STATUS(0);

    /* PPI control mode (assert on falling edge, 14 data bits, general purpose
       rx with 1 frame sync */
    bfin_write_PPI_CONTROL(PPI_MODE);

    return 0;
}

static int dma_init(void) {
    int ret;

    /* Request DMA channel */
    ret = request_dma(CH_PPI, DRIVER_NAME);
    if(ret < 0) {
        printk(KERN_WARNING DRIVER_NAME ": Could not allocate DMA channel\n");
        return ret;
    }

    /* Disable channel while it is being configured */
    disable_dma(CH_PPI);

    /* Allocate buffer space for the DMA engine to use */
    dma_buffer = __get_dma_pages(GFP_KERNEL, page_alloc_order(BUFFER_SIZE * BUFFER_COUNT));
    if(dma_buffer == 0) {
        printk(KERN_WARNING DRIVER_NAME ": Could not allocate dma_pages\n");
        free_dma(CH_PPI);
        return -ENOMEM;
    }

    /* Invalid caching on the DMA buffer */
    invalidate_dcache_range(dma_buffer, dma_buffer + (BUFFER_SIZE * BUFFER_COUNT));

    /* Set DMA configuration */
    set_dma_start_addr(CH_PPI, dma_buffer);
    set_dma_config(CH_PPI, (DMAFLOW_AUTO | WNR | RESTART | DI_EN | WDSIZE_16 | DMA2D | DI_SEL));
    set_dma_x_count(CH_PPI, SAMPLES_PER_BUFFER * CHANNELS);
    set_dma_x_modify(CH_PPI, SAMPLE_SIZE);
    set_dma_y_count(CH_PPI, BUFFER_COUNT);
    set_dma_y_modify(CH_PPI, SAMPLE_SIZE);
    set_dma_callback(CH_PPI, &buffer_full_handler, NULL);

    return 0;
}

static int device_init(void) {
    dev = cdev_alloc();
    dev->ops = &fops;
    dev->owner = THIS_MODULE;

    return cdev_add(dev, MKDEV(PPI_CHR_MAJOR, 0), 1);
}

static int __init ppi_adc_init(void) {
    int ret;
    
    ret = dma_init();
    if(ret) {
        return ret;
    }

    ret = ppi_init();
    if(ret) {
        dma_close();
        return ret;
    }
    
    ret = device_init();
    if(ret) {
        ppi_close();
        dma_close();
        return ret;
    }

    /* Disable everything */
    disable_dma(CH_PPI);
    bfin_write_PPI_CONTROL(bfin_read_PPI_CONTROL() & (~PORT_EN));

    SSYNC();

    return 0;
}

static void ppi_close(void) {
    bfin_write_PPI_CONTROL(0);
    peripheral_free_list(ppi_pins);
}

static void dma_close(void) {
    disable_dma(CH_PPI);
    free_pages(dma_buffer, page_alloc_order(BUFFER_SIZE * BUFFER_COUNT));
    free_dma(CH_PPI);
}

static void device_close(void) {
    cdev_del(dev);
}

static void __exit ppi_adc_close(void) {
    device_close();
    ppi_close();
    dma_close();
}

MODULE_LICENSE("GPL");
module_init(ppi_adc_init);
module_exit(ppi_adc_close);

/** \} */
