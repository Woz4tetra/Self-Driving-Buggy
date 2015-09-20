from serial_util import Board

board_ref = None


def _initBoard(address=None, baud=38400, disabled=False, upload=True,
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
    global board_ref

    board_ref = Board(address, baud, disabled, upload, sketchDir)

class Device(object):
    used_flags = set()

    def __init__(self, serial_flag, pin=None, pin_range=None):
        self.serialFlag = serial_flag

        Device._checkFlags(serial_flag)

        if pin_range is not None:
            if pin_range[0] <= pin <= pin_range[1]:
                self.pin = pin
            else:
                raise Exception(
                    "Invalid pin number! Valid pins for " + \
                    self.__class__.__name__ + \
                    " range from " + str(pin_range[0]) + "..." + str(
                        pin_range[1]) + "inclusive.")
        else:
            self.pin = pin

    def writeFlag(self):
        '''
        Writes the flag specified by the constructor's serialFlag parameter.

        :return: None
        '''
        board_ref.write(self.serialFlag)

    def writePin(self):
        '''
        If the constructor's pin parameter is not None, write the pin to serial.

        :return: None
        '''
        board_ref.write(chr(self.pin))

    def write(self, data):
        '''
        Writes the value to serial. If its an int, it is converted to a
        character (chr(value)). Only values 0...255 can be sent

        :param value:
        :return:
        '''
        if isinstance(data, int):
            board_ref.write(chr(data))
        else:
            board_ref.write(data)

    def writeBytes(self, data, byte_limit=None):
        '''

        :param value:
        :return:
        '''
        byte_count = 0

        while (data > 0 or byte_count == 0) and \
                (byte_count < byte_limit or byte_limit == None):
            # Will loop until all the data has been added or the byte_limit
            # has been hit

            self.write(data & 0xFF)
            data /= 0x100
            byte_count += 1

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
            return board_ref.readUntil()
        else:
            try:
                if outType == str:
                    return "".join(board_ref.readUntil()).split(strSeparation)
                elif outType == bool:
                    return bool(int(board_ref.readUntil()[-1]))
                else:
                    return outType("".join(board_ref.readUntil()))
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
        if flag in Device.used_flags:
            raise Exception("Duplicate flags! " + str(flag))
        else:
            Device.used_flags.add(flag)


class Servo(Device):
    def __init__(self, pin):
        self._position = 0

        super(Servo, self).__init__('s', pin, (1, 4))

    def _moveTo(self, position):
        self.writeFlag()  # flag
        self.writePin()  # pin
        self.writeBytes(position)  # position

    @staticmethod
    def _positionToBytes(position):
        position += 90
        return int(255.0 / 180 * position)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        self._position = new_position

        self._moveTo(Servo._positionToBytes(new_position))

class BuiltInLED(Device):
    def __init__(self, pin):
        self.isOn = False

        super(BuiltInLED, self).__init__('l', pin, (1, 4))

    def off(self):
        self.writeFlag()
        self.writePin()
        self.writeBytes(0)

        self.isOn = False

    def on(self):
        self.writeFlag()
        self.writePin()
        self.writeBytes(1)

        self.isOn = True

    def toggle(self):
        self.writeFlag()
        self.writePin()
        self.writeBytes(2)

        self.isOn = not self.isOn

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
