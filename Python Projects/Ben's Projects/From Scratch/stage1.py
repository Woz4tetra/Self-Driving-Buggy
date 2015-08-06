import time
import os

import serial

sketchDir = "Board"

os.system(
    "cd " + repr(sketchDir.strip("'")) + " && platformio run --target upload")

arduino = serial.Serial('/dev/cu.usbmodem1421', 38400, timeout=.1)
time.sleep(1)

arduino.write("Hello from Python!\n")

while True:
    data = arduino.readline()
    if data:
        print data
