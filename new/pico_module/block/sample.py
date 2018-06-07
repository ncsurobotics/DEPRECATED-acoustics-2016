# sample pico python file
import pico_module as pm
import csv
import matplotlib.pyplot as plt

"""
for mor info, see pico_module.c::pico_config()

this configures the pico scope for:
  4 channels
  trigger on rising edge
  trigger at ADC count threshold 3200 (or about 10% of the max voltage)
  200 samples
  voltage: 500MV
  sample interval of 1 time unit
  time unit: milliseconds
"""
#this is commented out for right now. if you need to change settings,
#change them in pico_module.c. They are the defined constants towards the top.
#temp = pm.pico_config(1, 2, 3200, 500, 1, 1, 4)
#print temp + "\n"

# initialize the picoscope with debugging and get the unit handle
handle = pm.pico_init(1)

# get the data after the next trigger. data will be a 2d list: 4x500
# this can be repeated as many times as needed
data = pm.pico_get_data(handle)

# process the data
# here we'll just print it
#for i in range(0, len(data)):
#    print "%6s" % (chr(i + 65)),
#print "\n"

# outer array is 4 elements
# inner array is the number of samples

#for i in range(0, len(data[0])):
#    for j in range(0, len(data)):
#        print "%6d" % data[j][i],
#    print "\n"
#print "\n"

# get the transpose (writes to file better)
data = zip(*data)
# write to file
with open("data.csv", "w+") as outData:
    wr = csv.writer(outData,delimiter=',')
    wr.writerow([pm.pico_get_sample_interval()])
    wr.writerows(data)

# close the picoscope.
# IF THIS STEP IS NOT DONE and you lose the handle, you will 
# need to power cycle the picoscope (unplug/replug usb)
pm.pico_close(handle)

plt.plot(data)
plt.show()
