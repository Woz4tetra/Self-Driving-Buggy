import serial
import time

ser = serial.Serial('/dev/cu.usbmodem1452', 9600, timeout=0.1)

while True:
    data = ""
    char = ser.read()
    while char != '\n':
        data += char
        char = ser.read()
    print data
    time.sleep(0.1)
    ser.write('a')