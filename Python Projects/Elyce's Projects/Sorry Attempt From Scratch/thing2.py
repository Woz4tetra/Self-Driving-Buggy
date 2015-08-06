from __future__ import print_function
import time
import os
import serial



os.system('cd ' + 'Board' + ' && platformio run --target upload' )

thing = serial.Serial('/dev/cu.usbmodem1411', 38400)
time.sleep(1)

flagthing = thing.read()

while flagthing != "R":
	flagthing = thing.read()
	print(flagthing, end = '')

thing.write("Q")
thing.flushInput()
thing.flushOutput()
time.sleep(1)

while True:
	data = thing.readline()
	if data:
		print(data)