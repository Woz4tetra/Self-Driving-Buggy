'''
This module contains all arduino communication methods and classes.

Example usage:
arduino.initBoard()
stepper = arduino.Stepper(1)
IMU = arduino.IMU()

while True:
    accel, gyro, dt = IMU.getIMU()
    stepper.moveTo(100)

For more details on...
    how Stepper and IMU work, type help(arduino.Device).
    what initBoard does, type help(arduino.initBoard) and help(arduino.Board)

Dependencies:
- platformio: http://platformio.org/#!/
- pyserial: https://pypi.python.org/pypi/pyserial
'''

import os
from sys import platform as _platform
import time
import math

import serial

arduino = None


def initBoard(address=None, baud=38400, disabled=False, upload=True,
              sketchDir=''):
    '''
    All instances of Peripherals reference one instance of arduino. Call
    initBoard once in your main code.

    :param address: The USB serial address reference. example on mac:
            dev/cu.usbmodem1411
    :param baud: This rate (int, long) must match the number contained in the
            arduino sketch (specified by sketchDir) ex. Serial.begin(38400);
    :param disabled: If you want to run your code without commenting out
            all objects that use arduino, set this to True
    :param disabled: If you want to upload the arduino sketch before running
            your code.
    :param sketchDir: The directory of the arduino sketch to upload starting
            from the project directory
    :return: None
    '''
    global arduino

    arduino = Board(address, baud, disabled, upload, sketchDir)
    return arduino


class Board(object):
    def __init__(self, address=None, baud=38400, disabled=False, upload=True,
                 sketchDir=''):
        '''
        initBoard initializes this class to the arduino variable. It contains
        the pySerial object reference and methods to write bytes to serial.
        This class will automatically find the arduino address (not implemented
        on windows or linux yet).

        :param address: An address will be automatically chosen if None.
                Otherwise, if a string is provided, that address will be used
        :param baud: This rate (int, long) must match the number contained in
                the file in Board/src/ ex. Serial.begin(38400);
        :param disabled: If you want to run your code without commenting out
                all objects that use arduino, set this to True
        :return: Instance of Board
        '''

        self.address = address
        self.baud = baud
        self.timeout = 0.1
        self.disabled = disabled
        self.sketchDir = sketchDir

        if self.disabled == False:
            if upload == True:
                os.system("cd arduino/" + repr(self.sketchDir.strip("'")) + \
                          " && platformio run --target upload")

            self._initSerial(self.address, self.baud, self.timeout)
            self._handshake()
        else:
            print("------------------------------")
            print("Arduino is disabled! (by user)")
            print("------------------------------")
            time.sleep(1)
    
    def _handshake(self):
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
    
    def _initSerial(self, address, baud, timeout):
        '''
        An internal method used by the constructor of Board. The variable
        serialReference is referenced.

        :param address: An address will be automatically chosen if None.
                Otherwise, if a string is provided, that address will be used
        :param baud: This rate (int, long) must match the number contained in
                the file in Board/src/ ex. Serial.begin(38400);
        :param timeout: Number of seconds (int, long) before serial.write
                or serial.read stops searching if no response is detected
        :return: None
        '''
        if address is None:
            for possibleAddress in Board._possibleAddresses():
                try:
                    self.serialReference = serial.Serial(possibleAddress, baud,
                                                         timeout=timeout,
                                                         interCharTimeout=timeout)
                    self.address = possibleAddress
                except:
                    pass
            if self.address is None:
                raise Exception(
                    "No Arduinos could be found! Did you plug it in? Try \
entering the address manually.")
        else:
            self.serialReference = serial.Serial(address, baud, timeout=timeout,
                                                 interCharTimeout=timeout)
        print("Initialized at address: " + self.address)

    @staticmethod
    def _possibleAddresses():
        '''
        An internal method used by _initSerial to search all possible
        USB serial addresses.
        Windows and Linux has not been implemented.

        :return: A list of strings containing all likely addresses
        '''
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

    def write(self, data):
        '''
        If the Arduino is not disabled (specified by constructor), this method
        will write the data parameter to serial.

        :param data: A string containing the data you want to write. If you want
                to write numbers to serial, it's recommended that you call
                chr before writeSerial. Ex. writeSerial(chr(9))
        :return: None
        '''
        if self.disabled == False:
            self.serialReference.write(data)

    def read(self):
        '''
        If the Arduino is not disabled (specified by constructor), this method
        will return the first character from serial

        :return: a string containing the serial data
        '''
        if self.disabled == False:
            return self.serialReference.read()

    def readUntil(self, endChar='\n'):
        '''
        If the Arduino is not disabled (specified by constructor), this method
        will keep reading until the '\\n' char is read. This method returns a
        list of all the characters found

        :return: a list containing all read characters excluding the new line
        '''
        if self.disabled == False:
            char = None
            data = []
            while char != endChar:
                char = self.serialReference.read()
                data.append(char)
            if len(data) > 1:
                return data[:-1]
        return []

    def stop(self):
        '''
        Sends the stop character (by my convention) to the file contained in
        the Arduino sketch (specified by sketchDir).
        (Subject to change:) Stops all stepper motors

        :return: None
        '''
        self.write('z')


class Device(object):
    usedFlags = set()

    def __init__(self, serialFlag, pin=None, pinRange=None):
        self.serialFlag = serialFlag

        Device._checkFlags(serialFlag)

        if pinRange is not None:
            if pinRange[0] <= pin <= pinRange[1]:
                self.pin = pin
            else:
                raise Exception(
                    "Invalid pin number! Valid pins for " + \
                    self.__class__.__name__ + \
                    " range from " + str(pinRange[0]) + "..." + str(
                        pinRange[1]) + "inclusive.")
        else:
            self.pin = pin

    def writeFlag(self):
        '''
        Writes the flag specified by the constructor's serialFlag parameter.

        :return: None
        '''
        arduino.write(self.serialFlag)

    def writePin(self):
        '''
        If the constructor's pin parameter is not None, write the pin to serial.

        :return: None
        '''
        arduino.write(chr(self.pin))

    def write(self, data):
        '''
        Writes the value to serial. If its an int, it is converted to a
        character (chr(value)). Only values 0...255 can be sent

        :param value:
        :return:
        '''
        if isinstance(data, int):
            arduino.write(chr(data))
        else:
            arduino.write(data)

    def writeBytes(self, data):
        '''
        Writes data to serial. Unlike, self.write(), writeBytes can send
        three bytes of data at time. This allows for a range from
        0...16,777,216.

        :param value:
        :return:
        '''
        bytes = [0, 0, 0]
        for index in xrange(3):
            bytes[index] = data % 0x100
            data /= 0x100
        for index in xrange(2, -1, -1):
            self.write(bytes[index])

    def read(self, outType=None, strSeparation=","):
        '''
        Reads from serial. If an outType is not specified, it will return a list
         of strings containing the read data. It will read until it finds a '\\n'
         character.

        If the outType is str, it will join the data and split it
         according to the strSeparation parameter. For example:
            ['1', '1', '0', ',', '4', '5', ',', '-', '6', '5']
                becomes...
            ['110', '45', '-64']

        If the outType is int, float or long, it will join the data and then
        convert it to int, float, or long respectively.
         For example:
            ['1', '1', '0'] becomes 110
        If it fails, it returns -1

        If the outType is bool, it will take the first value of the data read,
         convert it to int then into bool. If it fails, it returns False

        :param outType: An object of type "type." Can be int, float, long,
                str, or bool
        :param strSeparation: The character to separate the data by if
                outType is str.
        :return: The data read according to outType.
        '''
        if outType is None:
            return arduino.readUntil()
        else:
            try:
                if outType == str:
                    return "".join(arduino.readUntil()).split(strSeparation)
                elif outType == bool:
                    return bool(int(arduino.readUntil()[-1]))
                else:
                    return outType("".join(arduino.readUntil()))
            except:
                if outType == str:
                    return ""
                elif outType == bool:
                    return False
                elif outType == int or outType == float or outType == long:
                    return -1

    @staticmethod
    def _checkFlags(flag):
        '''
        An internal method used to check if any flags are duplicated.
        It uses the class variable usedFlags.

        :param flags: a list of single character strings
        :return: None. If a duplicate is found, an Exception is raised.
        '''
        if flag in Device.usedFlags:
            raise Exception("Duplicate flags! " + str(flag))
        else:
            Device.usedFlags.add(flag)


class Stepper(Device):
    def __init__(self, pin):
        self.speed = 0
        self.position = 0

        super(Stepper, self).__init__('s', pin, (1, 2))

    def goalReached(self):
        self.writeFlag()
        self.write(0)
        self.writePin()
        return self.read(bool)

    def moveTo(self, position):
        self.writeFlag()  # flag
        self.write(1)     # selector
        self.writePin()   # pin
        self.writeBytes(position)  # position

        self.position = position

    def setSpeed(self, speed):
        self.writeFlag()
        self.write(2)
        self.writePin()
        self.writeBytes(speed)

        self.speed = speed


class Vector(object):
    def __init__(self, x, y, z):
        '''
        A 3D vector used in the IMU class.

        :param x: int, float, or long
        :param y: int, float, or long
        :param z: int, float, or long
        :return: Instance of Vector
        '''
        self.x = x
        self.y = y
        self.z = z

    @property
    def roll(self):
        return self.x

    @roll.setter
    def roll(self, value):
        self.x = value

    @property
    def pitch(self):
        return self.y

    @pitch.setter
    def pitch(self, value):
        self.y = value

    @property
    def yaw(self):
        return self.z

    @yaw.setter
    def yaw(self, value):
        self.z = value

    def __repr__(self):
        return "<Vector> {%s, %s, %s}" % (self.x, self.y, self.z)

    def __len__(self):
        return len(self.__dict__)


class IMU(Device):
    scales = {
        "2g": 16384,
        "4g": 8192,
        "8g": 4096,
        "16g": 2048
    }

    def __init__(self):
        self.accel = Vector(0, 0, 0)
        self.gyro = Vector(0, 0, 0)
        self.dt = 0

        self.length = len(self.accel) + len(self.gyro) + 1

        super(IMU, self).__init__('i')

    def getData(self):
        self.writeFlag()
        stringData = self.read(str)
        if stringData == ['']:
            return [0] * self.length

        rawData = []
        for index in xrange(len(stringData)):
            try:
                rawData.append(float(stringData[index]))
            except:
                rawData.append(0)

        if len(rawData) != self.length:
            return

        gyro = []
        for axis in rawData[0:len(self.accel)]:
            gyro.append(axis * math.pi / 180)
        accel = []
        for axis in rawData[len(self.accel):
                len(self.accel) + len(self.gyro)]:
            accel.append(axis / IMU.scales['2g'] * 9.81)
        self.accel.x, self.accel.y, self.accel.z = accel  # m/s
        self.gyro.x, self.gyro.y, self.gyro.z = gyro  # radians
        self.dt = rawData[-1]

        return self.accel, self.gyro, self.dt


class Magnetometer(Device):
    def __init__(self):
        self.magnet = Vector(0, 0, 0)

        self.length = len(self.magnet)

        super(Magnetometer, self).__init__('m')

    def getData(self):
        self.writeFlag()
        stringData = self.read(str)
        if stringData == ['']:
            return [0] * self.length

        rawData = []
        for index in xrange(len(stringData)):
            try:
                rawData.append(float(stringData[index]))
            except:
                rawData.append(0)

        self.magnet.x, self.magnet.y, self.magnet.z = rawData

        return self.magnet



