
import os

from board.arduino_object import *


class IMU(Getter):
    def __init__(self):
        self.accelX, self.accelY, self.accelZ = 0, 0, 0
        self.gyroX, self.gyroY, self.gyroZ = 0, 0, 0
        super(IMU, self).__init__("ACCELGYRO_ID", "#### #### #### #### #### ####", "dec")

    def get(self):
        if self.send() and self.result != None:
            self.accelX, self.accelY, self.accelZ, \
                self.gyroX, self.gyroY, self.gyroZ = self.result


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
        if type(value) == str:
            self.send(self.positions[value])
        else:
            self.send(value)

    def __getitem__(self, item):
        return self.positions[item]

class Led13(Setter):
    def __init__(self):
        self.state = False
        super(Led13, self).__init__("LED13_ID", out_format='bool')

    def set(self, value):
        self.state = value
        return self.send(int(value))

def _add_defines(): # TODO: Add "enables" editing as well as ID editing
    project_dir = os.path.dirname(os.path.realpath(__file__))
    project_name = "Self-Driving Buggy Rev. 6"
    project_dir = project_dir[:project_dir.rfind(project_name) + len(
        project_name)]

    with open(project_dir + '/board/arduino/src/SerialBox.ino',
              'r') as serial_box_file:
        contents = serial_box_file.read()

        start = contents.find("/* Command IDs start */")
        end = contents.find("/* Command IDs end */", start)

        assert start != -1 and start < end

        defines = "/* Command IDs start */\n"

        for index in xrange(len(ArduinoObject.used_command_ids)):
            if index < 0x10:
                value = "0x0" + hex(index)[2:]
            else:
                value = hex(index)[0:2]

            defines += "#define " + ArduinoObject.used_command_ids[
                index] + " " + value + "\n"

        contents = contents[0: start] + defines + contents[end:]
    with open(project_dir + '/board/arduino/src/SerialBox.ino',
              'w') as serial_box_file:
        serial_box_file.write(contents)


def initialize(upload=True):
    _add_defines()

    if upload:
        os.system("cd .. && cd board/arduino && platformio run --target upload")

    start()
