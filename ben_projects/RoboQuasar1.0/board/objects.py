# object wrappers for sensors and commands

from data import Sensor
from data import Command

class IMU(Sensor):
    def __init__(self, sensor_id):
        super(IMU, self).__init__(sensor_id,
                                  'i8', 'i8', 'i8',
                                  'i8', 'i8', 'i8',
                                  'i8', 'i8', 'i8')

    @property
    def yaw(self):
        return self.data[-1]

class GPS(Sensor):
    def __init__(self, sensor_id):
        super(GPS, self).__init__(sensor_id, 'f', 'f', 'f', 'f', 'u8', 'u8')

    @property
    def long(self):
        return self.data[0]

    @property
    def lat(self):
        return self.data[1]

    @property
    def speed(self):
        return self.data[2]

    @property
    def heading(self):
        return self.data[3]

    @property
    def quality(self):
        return self.data[4:]

class Encoder(Sensor):
    def __init__(self, sensor_id):
        super(Encoder, self).__init__(sensor_id, 'u64')

    @property
    def distance(self):
        return self.data[0]

class Servo(Command):
    def __init__(self, command_id):
        super(Servo, self).__init__(command_id, 'u8')


class Led13(Command):
    def __init__(self, command_id):
        super(Led13, self).__init__(command_id, 'b')

