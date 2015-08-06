import os
import time
import serial

arduino = None

class Board(object):
    def __init__(self, address='/dev/cu.usbmodem1411', baud=38400, sketchDir='',
                 upload=True):
        if upload == True:
            os.system("cd .. && cd " + repr(
                sketchDir.strip("'")) + " && platformio run --target upload")

        self.address = address
        self.baud = baud
        self.timeout = 0.1
        self.sketchDir = sketchDir

        self.initSerial()
        self.handshake()

    def initSerial(self):
        self.serialReference = serial.Serial(self.address, self.baud,
                                             timeout=self.timeout)
        print("Initialized at address: " + self.address)

    def handshake(self):
        readFlag = self.serialReference.read()

        print("Waiting for ready flag...")
        time.sleep(1)
        while readFlag != 'R':
            readFlag = self.serialReference.read()
            print repr(readFlag)

        self.serialReference.write("P")
        self.serialReference.flushInput()
        self.serialReference.flushOutput()
        time.sleep(0.1)
        print("Arduino initialized!")

    def write(self, data):
        self.serialReference.write(data)

    def read(self):
        return self.serialReference.read()

    def readUntil(self, endChar='\n'):
        char = None
        data = []
        while char != endChar:
            char = self.serialReference.read()
            data.append(char)
        if len(data) > 1:
            return data[:-1]

        return []
