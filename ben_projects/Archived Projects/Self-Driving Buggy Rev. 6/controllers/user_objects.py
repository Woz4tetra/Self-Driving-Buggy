from board.arduino_object import *
import math


# class AccelGyro(Getter):
#     def __init__(self, simple_mode=True):
#         self.accelX, self.accelY, self.accelZ = 0, 0, 0
#         self.gyroX, self.gyroY, self.gyroZ = 0, 0, 0
#         self.simpleMode = simple_mode
#         if self.simpleMode:
#             super(AccelGyro, self).__init__("ACCELGYRO_ID",
#                                             "#### #### #### #### #### #### ####",
#                                             "dec")
#         else:
#             super(AccelGyro, self).__init__("ACCELGYRO_ID",
#                                             "######## ######## ########",
#                                             "float")
#
#     def get(self):
#         if self.send() and self.result != None:
#             # if self.simpleMode:
#             #     self.accelX, self.accelY, self.accelZ, \
#             #     self.gyroX, self.gyroY, self.gyroZ = self.result
#             # else:
#             #     self.gyroX, self.gyroY, self.gyroZ = self.result
#             return self.result
#
#
# class Magnet(Getter):
#     def __init__(self):
#         self.x, self.y, self.z = 0, 0, 0
#
#         super(Magnet, self).__init__("MAGNET_ID", "#### #### #### ####", "dec")
#
#
#     def get(self):
#         if self.send() and self.result != None:
#             # self.x, self.y, self.z = self.result
#             return self.result

class Accelerometer(Getter):
    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0
        super(Accelerometer, self).__init__("ACCEL",
                                            "#### #### ####",
                                            "int")

    def get(self):
        if self.send() and self.result != None:
            # for index in xrange(len(self.result)):
            #     self.result[index] = float(self.result[index]) / 16384
            self.x, self.y, self.z = self.result
        return self.x, self.y, self.z


class Gyroscope(Getter):
    def __init__(self):
        self.roll, self.pitch, self.yaw = 0, 0, 0
        super(Gyroscope, self).__init__("GYRO",
                                        "#### #### ####",
                                        "int")

    def get(self):
        if self.send() and self.result != None:
            # for index in xrange(len(self.result)):
            #     self.result[index] = float(self.result[index]) * 250 / 32768
            self.roll, self.yaw, self.pitch = self.result
        return self.roll, self.pitch, self.yaw


class Magnetometer(Getter):
    def __init__(self):
        self.roll, self.pitch, self.yaw = 0, 0, 0
        super(Magnetometer, self).__init__("MAGNET",
                                           "#### #### ####",
                                           "int")

    def get(self):
        if self.send() and self.result != None:
            # for index in xrange(len(self.result)):
            #     self.result[index] = float(self.result[index]) * 1200 / 4096
            self.roll, self.yaw, self.pitch = self.result
        return self.roll, self.pitch, self.yaw


class GPS(Getter):
    def __init__(self):
        self.speed = 0
        self.angle = 0
        self.coordinates = [0, 0]  # latitude, longitude
        self.satellites, self.fix_quality = 0, 0
        super(GPS, self).__init__("GPS",
                                  "######## ######## ######## ######## ## ##",
                                  "ffffuu")

    def get(self):
        if self.send() and self.result != None:
            self.coordinates[0], self.coordinates[
                1], self.angle, self.speed, self.satellites, self.fix_quality = self.result

            # return self.coordinates


class Encoder(Getter):
    def __init__(self, initial_position=(0, 0)):
        self.counts0 = 0
        self.counts1 = 0
        self.position = list(initial_position)

        super(Encoder, self).__init__("ENCODER")

    def get(self, angle_yaw):
        if self.send() and self.result != None:
            self.counts1 = self.result

            self.position[0] += math.cos(angle_yaw) * (
                self.counts1 - self.counts0)
            self.position[1] += math.sin(angle_yaw) * (
                self.counts1 - self.counts0)
            self.counts0 = self.counts1

        return self.position


class Servo(Setter):
    def __init__(self, **positions):
        self.positions = positions
        super(Servo, self).__init__("SERVO")

    @property
    def value(self):
        if self.result != None:
            return self.result
        else:
            return 0

    def set(self, value):
        if type(value) == str and (value in self.positions.keys()):
            self.send(int(self.positions[value]))
        elif type(value) == int:
            self.send(value)
        elif value.isdigit():
            self.send(int(value))

    def toggle(self, value1, value2):
        if value1 in self.positions.keys():
            value1 = self.positions[value1]
        if value2 in self.positions.keys():
            value2 = self.positions[value2]

        if self.result != value1:
            self.set(value1)
        else:
            self.set(value2)

    def __getitem__(self, item):
        return self.positions[item]


class Led13(Setter):
    def __init__(self):
        self.state = False
        super(Led13, self).__init__("LED13", out_format='bool')

    def set(self, value):
        self.state = bool(value)

        return self.send(int(self.state))

    def toggle(self):
        return self.set(not self.state)