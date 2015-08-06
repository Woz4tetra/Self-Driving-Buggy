'''
This module contains all arduino communication methods and classes.

Example usage:
arduino.initBoard()
dcmotor = arduino.DCMotor(1)
IMU = arduino.IMU()

while True:
    accel, gyro, dt = IMU.getIMU()
    dcmotor.driveForward(100)

For more details on...
    how DCMotor and IMU work, type help(arduino.Device).
    what initBoard does, type help(arduino.initBoard) and help(arduino.Board)
    
Dependencies:
- platformio: http://platformio.org/#!/
- pyserial: https://pypi.python.org/pypi/pyserial
'''
import time
import sys
import glob
import os
import math

import serial



arduino = None


def initBoard(address=None, baud=38400, disabled=False, upload=False,
              uploadOnly=False):
    '''
    All instances of Peripherals reference one instance of arduino. Call
    initBoard once in your main code.

    :param address: The USB serial address reference. example on mac:
            dev/cu.usbmodem1411
    :param baud: This rate (int, long) must match the number contained in the
            file in Board/src/ ex. Serial.begin(38400);
    :param disabled: If you want to run your code without commenting out
            all objects that use arduino, set this to True
    :param upload: If True, the ino file in Board/src will be uploaded then
            the code after it will run
    :param uploadOnly: If True, the ino file in Board/src will be uploaded and
            the program will end
    :return: None
    '''
    global arduino

    if upload is True or uploadOnly is True:
        os.system("cd Board && platformio run --target upload")

    if uploadOnly is False:
        arduino = Board(address, baud, disabled)
    else:
        quit()


class Board(object):
    def __init__(self, address=None, baud=38400, disabled=False):
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
        self.timeout = 2
        self.disabled = disabled

        if self.disabled == False:
            self._initializeSerial(self.address, self.baud, self.timeout)

            print("Initialized at address: " + self.address)

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
        else:
            print("------------------------------")
            print("Arduino is disabled! (by user)")
            print("------------------------------")
            time.sleep(1)

    def _initializeSerial(self, address, baud, timeout):
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
                    print possibleAddress
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

    @staticmethod
    def _possibleAddresses():
        '''
        An internal method used by _initializeSerial to search all possible
        USB serial addresses.
        Windows and Linux has not been implemented.

        :return: A list of strings containing all likely addresses
        '''
        if sys.platform.startswith("darwin"):  # OS X
            devices = os.listdir("/dev/")
            arduinoDevices = []
            for device in devices:
                if device.find("cu.usbmodem") > -1:
                    arduinoDevices.append("/dev/" + device)
            return arduinoDevices
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # linux
            return glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('win'):  # Windows
            return ['COM' + str(i + 1) for i in range(256)]
        else:
            raise EnvironmentError('Unsupported platform')

    def writeSerial(self, data):
        '''
        If the arduino is not disabled (specified by constructor), this method
        will write the data parameter to serial.

        :param data: A string containing the data you want to write. If you want
                to write numbers to serial, it's recommended that you call
                chr before writeSerial. Ex. writeSerial(chr(9))
        :return: None
        '''
        if self.disabled == False:
            self.serialReference.write(data)

    def readSerial(self):
        '''
        If the arduino is not disabled (specified by constructor), this method
        will keep reading until the '\\n' char is read. This method returns a
        list of all the characters found

        :return:
        '''

        if self.disabled == False:
            char = None
            data = []
            while char != "\n":
                char = self.serialReference.read()
                data.append(char)
            if len(data) > 1:
                return data[:-1]
        return []

    def stop(self):
        '''
        Sends the stop character (by my convention) to the file contained in
        Board/src/. (Subject to change:) Stops all motors.

        :return: None
        '''
        self.writeSerial('z')


class Device(object):
    usedFlags = set()

    def __init__(self, serialFlag, pin=None, pinRange=None):
        '''
        This class and all subclasses act as wrappers for serial. Here's a
         breakdown of the conventions used: In the file contained in Board/src/,
         a byte from serial is read. This byte acts as a command pointing to
         various parts of the arduino code.

            Example 1: Return data

        char incomingByte = Serial.read();
        delay(5);
        if (incomingByte == 'a')  // Send accel & gyro data over serial
        {
            Serial.print(ypr[2] * 180/M_PI); Serial.print(',');
            Serial.print(ypr[1] * 180/M_PI); Serial.print(',');
            Serial.print(ypr[0] * 180/M_PI); Serial.print('\\n');
        }

        So if a subclass of Device wants to be associated with this code, it
         should call super(Subclass, self).__init__('a') in __init__
         and self.writeFlag() in a custom method.

        If a subclass wants to read the above printed serial data, call
         self.read() in the aforementioned custom method. An example of what it
         will return is this:
            ['1', '1', '0', ',', '4', '5', ',', '-', '6', '5']

        If you want to return proper data, call self.read(str). It will now
         return ['110', '45', '-64'].

        If the data is separated by something other than a comma, you can
         provide a string to the strSeparation parameter:
            self.read(str, ']')

        If you want the data in a different form, you can provide
         the int or bool types as parameters.


            Example 2: Series of commands

        Some subclasses Device require data (like pin numbers and other data)
         to be set to the arduino sketch. The DCMotor is a good example here.
         This is arduino sketch for the dc motor command:
            else if (incomingByte == 'c')
            {
                uint8_t motorPin = (uint8_t)Serial.read(); # *1
                motorSpeeds[motorPin - 1] = (uint8_t)Serial.read(); # *2

                if (motorPin == 1) {
                    motor1.run(FORWARD);
                    motor1.setSpeed(motorSpeeds[motorPin - 1]);
                }
            }
         If you look in the above example, you'll notice a pin is provided. You
          can command that pin to line *1 by calling self.writePin().
          Furthermore, you can command a speed to line *2 by calling
          self.write(an int from 0...255)
         The method _drive therefore looks like this:
         def _drive(self):
            self.writeFlag(self.forward)
            self.writePin()
            self.write(self.speed)

        :param serialFlags: a single character string or a dictionary with
                values of single character strings
        :param pin: an optional int parameter. If specified, the method
                self.writePin() will write that number to serial
        :param pinRange: an optional iterable of size 2. Acts as a range for
                the pin parameter. If None, no check is made
        :return: Instance of Device
        '''

        self.serialFlag = serialFlag

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

    @staticmethod
    def _checkFlags(flags):
        '''
        An internal method used to check if any flags are duplicated.
        It uses the class variable usedFlags which is a set.

        :param flags: a list of single character strings
        :return: None. If a duplicate is found, an Exception is raised.
        '''
        flagSet = set(flags)
        if len(flags) != len(flagSet):
            raise Exception("Duplicate flags!")

        if (Device.usedFlags - flagSet) != Device.usedFlags:
            raise Exception("Flag(s) occupied! " + str(
                list(Device.usedFlags.intersection(flagSet))))

    def writeFlag(self):
        '''
        writes the flag specified by the constructor's serialFlag parameter.
        If serialFlag is a dictionary, flagName should be the key of the flag.
        Otherwise, it should be left blank.

        :param flagName: The key of the flag if Device uses multiple flags
        :return: None
        '''
        arduino.writeSerial(self.serialFlag)

    def writePin(self):
        '''
        If the constructor's pin parameter is not None, write the pin to serial.

        :return: None
        '''
        if self.pin is not None:
            arduino.writeSerial(chr(self.pin))

    def write(self, value):
        '''
        Writes the value to serial. If its an int, it is converted to a
        character (chr(value)).

        :param value:
        :return:
        '''
        if isinstance(value, int):
            arduino.writeSerial(chr(value))
        else:
            arduino.writeSerial(value)

    def writeBytes(self, data):
        bytes = []
        while data > 0:
            byte = data % 0x100
            data /= 0x100
            bytes.append(byte)
        for byte in bytes[::-1]:
            arduino.writeSerial(chr(byte))

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
            return arduino.readSerial()
        else:
            try:
                if outType == str:
                    return "".join(arduino.readSerial()).split(strSeparation)
                elif outType == bool:
                    return bool(int(arduino.readSerial()[-1]))
                else:
                    return outType("".join(arduino.readSerial()))
            except:
                if outType == str:
                    return ""
                elif outType == bool:
                    return False
                elif outType == int or outType == float or outType == long:
                    return -1


class DCMotor(Device):
    directions = {
        "forward": 1,
        "backward": 2,
        "brake": 3,
        "release": 4
    }

    def __init__(self, pin):
        self.speed = 0
        self.direction = "forward"

        super(DCMotor, self).__init__('c', pin, (1, 4))

    def drive(self, speed, direction):
        self.writeFlag()
        self.writePin()
        self.write(DCMotor.directions[direction])
        self.write(speed)

        self.speed = speed

    def forward(self, speed):
        self.drive(speed, "forward")

    def backward(self, speed):
        self.drive(speed, "backward")

    def reverse(self):
        if self.direction == "forward":
            self.direction = "backward"
        else:
            self.direction = "forward"

        self.drive(self.speed, self.direction)

    def stop(self):
        self.drive(0, "release")

class Stepper(Device):
    modes = {
        "single": 1,
        "double": 2,
        "interleave": 3,
        "microstep": 4,
    }
    def __init__(self, pin):
        self._position = 0

        super(Stepper, self).__init__('d', pin, (1, 2))

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if value < 0:
            value = 0
        if value > 2 ** 16:
            value = 2 ** 16

        self._position = value

    def moveTo(self, steps, rpm):
        self.writeFlag()
        self.writePin()

        self.write(steps)
        self.write(rpm)


class Servo(Device):
    def __init__(self, pin):
        super(Servo, self).__init__('e', pin)

    def set(self, position):
        self.writeFlag()
        self.writePin()
        self.write(position)

class Button(Device):
    def __init__(self, pin):
        '''
        A subclass of Device and abides by its conventions. See the help
        for its constructor for more details. Uses the 'f' flag.

        :param pin: The pin to be used by self.writePin()
        :return: Instance of DCMotor
        '''

        self.previous = False
        self.state = False
        super(Button, self).__init__('b', pin=pin, pinRange=(0, 13))

    def _update(self):
        '''
        An internal method used to update the current and previous states of
        the button

        :return: None
        '''
        self.writeFlag()
        self.writePin()
        self.previous = self.state
        self.state = self.read(bool)

    def getState(self):
        '''
        Updates the state of the button and returns it

        :return: bool of the button's current state
        '''
        self._update()
        return self.state

    def wasReleased(self):
        '''
        Using self.previous and self.state, this method checks if the button
         was released.

        :return: bool, True if released.
        '''
        self._update()
        return self.previous == True and self.state == False

    def wasPressed(self):
        '''
        Using self.previous and self.state, this method checks if the button
         was pressed.

        :return: bool, True if pressed.
        '''
        self._update()
        return self.previous == False and self.state == True


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
        '''
        A subclass of Device and abides by its conventions. See the help
        for its constructor for more details. Uses the 'a' flag.

        :return: Instance of IMU
        '''
        self.accel = Vector(0, 0, 0)
        self.gyro = Vector(0, 0, 0)
        self.magnet = Vector(0, 0, 0)
        self.dt = 0

        self.length = len(self.accel) + len(self.gyro) + len(self.magnet) + 1

        super(IMU, self).__init__('a')

    def getIMU(self):
        '''
        Reads data from serial. The IMU class expects the data to come as a
         list of 7 values. The first three are x, y, z for acceleration, the
         next three are the roll, pitch, and yaw for gyroscope, and the last
         value is the dt in milliseconds between samples.

        :return: A tuple of (<Vector>, <Vector>, int) containing the
                acceleration, gyroscope, and dt data respectively.
        '''
        if arduino is not None and arduino.disabled == False:
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
            magnet = []
            for axis in rawData[len(self.accel) + len(self.gyro):
                                len(self.accel) + len(self.gyro) + len(self.magnet)]:
                magnet.append(axis)

            self.accel.x, self.accel.y, self.accel.z = accel  # m/s
            self.gyro.x, self.gyro.y, self.gyro.z = gyro  # radians
            self.magnet.x, self.magnet.y, self.magnet.z = magnet
            self.dt = rawData[-1]

        return self.accel, self.gyro, self.magnet, self.dt

    def printData(self, format="readable"):
        if format == "excel":
            print "%s\t%s\t%s\t%s\t%s\t%s" % (
                self.accel.x, self.accel.y, self.accel.z, self.gyro.x,
                self.gyro.y,
                self.gyro.z)
        elif format == "readable":
            print "%2.3fg, %2.3fg, %2.3fg" % (
                self.accel.x, self.accel.y, self.accel.z)
            print "%2.3f,  %2.3f,  %2.3f" % (
                self.gyro.x, self.gyro.y, self.gyro.z)


class Sonar(Device):
    def __init__(self, pin):
        '''
        A subclass of Device and abides by its conventions. See the help
        for its constructor for more details. Uses the 'g' flag.

        :param pin: Not tied to a particular pin on the arduino. This pin
                specifies which sensor to get data from if there are multi sonar
                sensors.
        :return: Instance of Sonar
        '''
        super(Sonar, self).__init__('e', pin)

    def getDistance(self):
        '''
        Sends the serial flag and pin to serial in that order.

        :return: The distance in centimeters read from the ultrasonic sensor
        '''
        self.writeFlag()
        self.writePin()
        return self.read(int)
