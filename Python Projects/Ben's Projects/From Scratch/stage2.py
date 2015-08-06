from __future__ import print_function
import time
import os

import serial

# ----- serial setup ----- #

sketchDir = "Board/stage2"

os.system(
    "cd " + repr(sketchDir.strip("'")) + " && platformio run --target upload")

arduino = serial.Serial('/dev/cu.usbmodem1411', 115200, timeout=.1)
time.sleep(1)

# ----- serial handshake ----- #
readFlag = arduino.read()

print("Waiting for ready flag...")
time.sleep(1)
while readFlag != 'R':
    readFlag = arduino.read()
    print(readFlag, end="")

arduino.write("P")
arduino.flushInput()
arduino.flushOutput()
time.sleep(0.1)
print("Arduino initialized!")


# ----- serial communication ----- #

arduino.write("Hello from Python!\n")

while True:
    data = arduino.readline()
    if data:
        print(data, end="")
