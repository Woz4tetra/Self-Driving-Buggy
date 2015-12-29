"""
    Written by Ben Warwick

    objects.py, written for RoboQuasar1.0
    Version 12/24/2015
    =========

    Object wrappers for sensors and commands
    Each sensor handles its own data interpretation.

    Usage
    -----

    Dependencies
    ------------
    data.py
"""

import math
from .data import Sensor
from .data import Command

class TMP36(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'u16')

    @property
    def temperature(self):
        millivolts = 3300.0 / 1024 * self.data
        return (millivolts - 500) / 100

class MCP9808(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i16')

    @property
    def temperature(self):
        temperature = self.data & 0x0fff
        temperature /= 16.0
        if self.data & 0x1000:
            temperature -= 0x100
        return temperature

class GPS(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i16', 'f', 'i16', 'f', 'f', 'f', 'f')
    
    @property
    def latitude(self):
        return (self.data[0], self.data[1])
    
    @property
    def longitude(self):
        return (self.data[2], self.data[3])
    
    @property
    def speed(self):
        return self.data[4]
    
    @property
    def hdop(self):
        return self.data[5]
    
    @property
    def heading(self):
        if self.data[6] >= 348.75:
            return 360 - self.data[6]
        else:
            return self.data[6] + 11.25

class BuiltinAccel(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i8', 'i8', 'i8')
    
    @property
    def x(self):
        return self.data[0]

    @property
    def y(self):
        return self.data[1]

    @property
    def z(self):
        return self.data[2]

class Servo(Command):
    def __init__(self, command_id, initial=0, hard_bound=True):
        super().__init__(command_id, 'i8')
        self.data = initial
        if hard_bound:
            self.bound = self.hard_bound
        else:
            self.bound = self.loop_bound

    @property
    def degrees(self):
        return self.data

    def loop_bound(self, value):
        while value < -90:
            value += 90
        while value > 90:
            value -= 90
        return value

    def hard_bound(self, value):
        if value < -90:
            value = -90
        if value > 90:
            value = 90
        return value

    def set(self, degrees):
        self.data = self.bound(degrees)

    def offset(self, offset):
        self.data = self.bound(self.data + offset)
