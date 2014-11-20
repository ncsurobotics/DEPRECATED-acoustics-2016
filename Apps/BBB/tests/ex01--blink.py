import Adafruit_BBIO.GPIO as GPIO
from time import sleep

sleeptime = 0.5
target = "P8_14"

GPIO.setup(target, GPIO.OUT)
n = 0

while n<10:
	GPIO.output(target, GPIO.HIGH)
	sleep(sleeptime)
	GPIO.output(target,GPIO.LOW)
	sleep(sleeptime)
	n += 1

GPIO.cleanup
