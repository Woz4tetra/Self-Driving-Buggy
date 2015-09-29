import time
from sys import platform as _platform
import os

import serial

arduino = None


def initBoard(address=None, baud=38400, disabled=False, upload=False, uploadOnly=False):
    global arduino

    if upload is True or uploadOnly is True:
        os.system("cd Board && platformio run --target upload")

    if uploadOnly is False:
        arduino = Board(address, baud, disabled)


class Board(object):
    def __init__(self, address=None, baud=38400, disabled=False):
        self.address = address
        self.baud = baud
        self.timeout = 2
        self.disabled = disabled
        self.dataLength = 20

        if self.disabled == False:
            self._initializeSerial(self.address, self.baud, self.timeout)

            print("Initialized at address: " + self.address)

            readFlag = self.serialReference.read()

            print("Waiting for ready flag...")
            time.sleep(1)
            while readFlag != 'R':
                readFlag = self.serialReference.read()
                print repr(readFlag)
            print("Arduino initialized!")
        else:
            print("Arduino is disabled!")

    def _initializeSerial(self, address, baud, timeout):
        if address is None:
            for possibleAddress in Board._possibleAddresses():
                try:
                    self.serialReference = serial.Serial(possibleAddress, baud, timeout=timeout,
                                                         interCharTimeout=timeout)
                    self.address = possibleAddress
                except:
                    pass
            if self.address is None:
                raise Exception("No Arduinos could be found! Did you plug it in? Try entering the address manually.")
        else:
            self.serialReference = serial.Serial(address, baud, timeout=timeout, interCharTimeout=timeout)

    @staticmethod
    def _possibleAddresses():
        if _platform == "darwin":  # OS X
            devices = os.listdir("/dev/")
            arduinoDevices = []
            for device in devices:
                if device.find("cu.usbmodem") > -1:
                    arduinoDevices.append("/dev/" + device)
            return arduinoDevices
        elif _platform == "linux" or _platform == "linux2":  # linux
            raise NotImplementedError
            # return []
        elif _platform == "win32":  # Windows
            raise NotImplementedError
            # return []

    def writeSerial(self, data):
        self.serialReference.write(data)

    def readSerial(self):
        char = None
        data = []
        while char != "\n":
            char = self.serialReference.read()
            data.append(char)
        if len(data) > 1:
            return data[:-1]
        else:
            return []

    def stop(self):
        self.writeSerial('z')


# class LCD(object):
#     @staticmethod
#     def displayIMU():
#         arduino.writeSerial('b')


class DCMotor(object):
    def __init__(self, pin):
        if 1 <= pin <= 4:
            self.pin = pin
        else:
            raise Exception("Invalid pin number! Valid pins for DC motors range from 1...4 inclusive.")
        self.speed = 0
        self.directions = {
            True: 'c',  # forward
            False: 'd', # backward
            "stop": 'e'
        }
        self.forward = True
    
    @property
    def speed(self):
        return self.speed
    
    @setter
    def speed(self, value):
        if value > 255:
            self.speed = 255
        elif value < 0:
            self.speed = 0
        else:
            self.speed = value
    
    def reverse(self):
        self.forward = not self.forward
        self._drive()
    
    def _drive(self):
        arduino.writeSerial(self.directions[self.forward])
        arduino.writeSerial(chr(self.pin))
        arduino.writeSerial(chr(self.speed))

    def driveForward(self, speed):
        self.speed = speed
        self.forward = True
        self._drive()

    def driveBackward(self, speed):
        self.speed = speed
        self.forward = False
        self._drive()

    def stop(self):
        self.speed = 0
        arduino.writeSerial(self.directions["stop"])
        arduino.writeSerial(chr(self.pin))


class Button(object):
    def __init__(self, pin):
        if 0 <= pin <= 13:
            self.pin = pin
        else:
            raise Exception("Invalid pin number! Valid pins for buttons range from 0...13 inclusive.")

    def getState(self):
        arduino.writeSerial('f')
        arduino.writeSerial(chr(self.pin))
        try:
            return not bool(int(arduino.readSerial()[0]))
        except:
            return False


class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class IMU(object):
    scales = {
        "2g": 16384,
        "4g": 8192,
        "8g": 4096,
        "16g": 2048
    }

    def __init__(self):
        self.rawData = [0] * 7
        self.accel = Vector(0, 0, 0)
        self.gyro = Vector(0, 0, 0)
        self.dt = 0

    def getIMU(self):
        arduino.writeSerial('a')
        stringData = "".join(arduino.readSerial()).split(",")
        for index in xrange(len(stringData)):
            try:
                self.rawData[index] = float(stringData[index])
            except:
                self.rawData[index] = 0

        self.interpretRaw()

        return self.accel, self.gyro, self.dt

    def interpretRaw(self):
        gyro = []
        for axis in self.rawData[0:3]:
            gyro.append(axis)
        accel = []
        for axis in self.rawData[3:7]:
            accel.append(axis / IMU.scales['2g'])
        self.accel.x, self.accel.y, self.accel.z = accel
        self.gyro.x, self.gyro.y, self.gyro.z = gyro
        self.dt = self.rawData[-1]

    def printData(self, format="readable"):
        if format == "excel":
            print "%s\t%s\t%s\t%s\t%s\t%s" % (self.accel.x, self.accel.y, self.accel.z, self.gyro.x, self.gyro.y, self.gyro.z)
        elif format == "readable":
            print "%2.3fg, %2.3fg, %2.3fg" % (self.accel.x, self.accel.y, self.accel.z)
            print "%2.3f,  %2.3f,  %2.3f" % (self.gyro.x, self.gyro.y, self.gyro.z)

class Sonar(object):
    def getDistance(self):
        arduino.writeSerial('g')
        try:
            return int(arduino.readSerial())
        except:
            return -1

