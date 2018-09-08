import pico_module as pm
import csv
import matplotlib.pyplot as plt
import signal
import sys

handle = 0

def signal_handler(signal, frame):
  print "Stopping...\n"
  if ( handle != 0 ):
    pm.pico_close(handle);
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
handle = pm.pico_init(1)

i = 0
while (True):
  data = pm.pico_get_data(handle)
  # get the transpose (writes to file better)
  data = zip(*data)
  plt.plot(data)
  plt.show()
  # write to file
  #i += 1;
  #with open("orientation4/Test" + str(i) + ".csv", "w+") as outData:
  #    wr = csv.writer(outData,delimiter=',')
  #    wr.writerows(data)
