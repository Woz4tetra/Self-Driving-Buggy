from __future__ import print_function

import os
from sys import platform as _platform
import time

import serial


class Board(object):
    def __init__(self, address=None, baud=38400, disabled=False, upload=True,
                 sketchDir='', board_name='pyboard'):
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

        if self.disabled == False:
            if upload == True:
                if board_name == 'arduino':
                    self.sketchDir = sketchDir
                    os.system("cd arduino/" + repr(self.sketchDir.strip("'")) + \
                              " && platformio run --target upload")

            self._initSerial(self.address, self.baud, self.timeout)
            self._handshake()
        else:
            print("------------------------------")
            print(" Board is disabled! (by user)")
            print("------------------------------")
            time.sleep(1)

    def _handshake(self):
        readFlag = self.serialReference.read()

        print("Waiting for ready flag...")
        time.sleep(1)
        while readFlag != 'R':
            readFlag = self.serialReference.read()
            print(readFlag, end="")

        self.serialReference.write("P")
        time.sleep(0.1)
        self.serialReference.flushInput()
        self.serialReference.flushOutput()
        print("Board initialized!")

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
                    "No boards could be found! Did you plug it in? Try \
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
