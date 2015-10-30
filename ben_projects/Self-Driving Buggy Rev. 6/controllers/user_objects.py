from board.arduino_object import *
from board.arduino_object import _add_defines


class AccelGyro(Getter):
    def __init__(self, simple_mode=True):
        self.accelX, self.accelY, self.accelZ = 0, 0, 0
        self.gyroX, self.gyroY, self.gyroZ = 0, 0, 0
        self.simpleMode = simple_mode
        if self.simpleMode:
            super(AccelGyro, self).__init__("ACCELGYRO_ID",
                                            "#### #### #### #### #### #### ####",
                                            "dec")
        else:
            super(AccelGyro, self).__init__("ACCELGYRO_ID",
                                            "######## ######## ########",
                                            "float")

    def get(self):
        if self.send() and self.result != None:
            # if self.simpleMode:
            #     self.accelX, self.accelY, self.accelZ, \
            #     self.gyroX, self.gyroY, self.gyroZ = self.result
            # else:
            #     self.gyroX, self.gyroY, self.gyroZ = self.result
            return self.result


class Magnet(Getter):
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

        super(Magnet, self).__init__("MAGNET_ID", "#### #### #### ####", "dec")


    def get(self):
        if self.send() and self.result != None:
            # self.x, self.y, self.z = self.result
            return self.result


class GPS(Getter):
    def __init__(self):
        self.longitude, self.latitude, self.speed, self.angle = 0, 0, 0, 0
        self.satellites, self.fix_quality = 0, 0
        super(GPS, self).__init__("GPS_ID",
                                  "######## ########", "float")

    def get(self):
        if self.send() and self.result != None:
            self.longitude, self.latitude = self.result


class Encoder(Getter):
    def __init__(self):
        self.distance = 0
        super(Encoder, self).__init__("ENCODER_ID")

    def get(self):
        if self.send() and self.result != None:
            self.distance = self.result


class Servo(Setter):
    def __init__(self, **positions):
        self.positions = positions
        super(Servo, self).__init__("SERVO_ID")

    @property
    def value(self):
        return self.result

    def set(self, value):
        if type(value) == str and (value in self.positions.keys()):
            self.send(int(self.positions[value]))
        elif value.isdigit():
            self.send(int(value))

    def __getitem__(self, item):
        return self.positions[item]


class Led13(Setter):
    def __init__(self):
        self.state = False
        super(Led13, self).__init__("LED13_ID", out_format='bool')

    def set(self, value):
        self.state = value
        return self.send(int(value))


def initialize():
    _add_defines()

    # if upload:
    #     os.system("cd .. && cd board/arduino && platformio run --target upload")

    start()
