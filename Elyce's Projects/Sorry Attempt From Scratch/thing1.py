import time
import os
import serial

os.system( 'cd ' + 'Board' + '&& platformio run --target upload')
thing = serial.Serial( '/dev/cu.usbmodem1411', 38400)
time.sleep(1)

while True:
	thingy =  thing.readline()
	if thingy:
		print thingy