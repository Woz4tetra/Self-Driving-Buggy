from __future__ import print_function
import time
import os

import serial

# ----- serial setup ----- #

sketchDir = "Board/stage3"

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

def readUntil(endChar='\n'):
    '''
    If the Arduino is not disabled (specified by constructor), this method
    will keep reading until the '\\n' char is read. This method returns a
    list of all the characters found

    :return: a list containing all read characters excluding the new line
    '''
    char = None
    data = []
    while char != endChar:
        char = arduino.read()
        data.append(char)
    if len(data) > 1:
        return data[:-1]
    return []

while True:
    arduino.write('t')
#    print("".join(readUntil()))
    print(arduino.readline())

    time.sleep(0.5)

    arduino.write('v')

    time.sleep(0.5)

    arduino.write('p')
#    print("".join(readUntil()))
    print(arduino.readline())

    time.sleep(0.5)
