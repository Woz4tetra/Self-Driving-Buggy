import pyb
from pyb import I2C

import math

from libraries.micro_gps import MicropyGPS
from libraries.micro_encoder import MicroEncoder

from libraries.orientation.bmp085 import Barometer
from libraries.orientation.lsm303 import Accelerometer
from libraries.orientation.lsm303 import Magnetometer
from libraries.orientation.l3gd20 import Gyroscope

from data import *


class MCP9808(Sensor):
    CONFIG = 0x01
    CONFIG_SHUTDOWN = 0x0100
    CONFIG_CRITLOCKED = 0x0080
    CONFIG_WINLOCKED = 0x0040
    CONFIG_INTCLR = 0x0020
    CONFIG_ALERTSTAT = 0x0010
    CONFIG_ALERTCTRL = 0x0008
    CONFIG_ALERTSEL = 0x0004
    CONFIG_ALERTPOL = 0x0002
    CONFIG_ALERTMODE = 0x0001
    UPPER_TEMP = 0x02
    LOWER_TEMP = 0x03
    CRIT_TEMP = 0x04
    AMBIENT_TEMP = 0x05
    MANUF_ID = 0x06
    DEVICE_ID = 0x07

    def __init__(self, sensor_id, bus, addr=0x18):
        super().__init__(sensor_id, 'i16')
        self.bus = bus
        self.addr = addr

        self.i2c_ref = I2C(self.bus, I2C.MASTER)

        addresses = self.i2c_ref.scan()
        # print("Scanning devices:", [hex(x) for x in addresses])
        if self.addr not in addresses:
            raise Exception("MCP9808 is not detected")

        manuf_id = self.i2c_read_16(self.MANUF_ID)
        if manuf_id != 0x0054:
            raise Exception("Invalid manufacture ID!", manuf_id)

        device_id = self.i2c_read_16(self.DEVICE_ID)
        if device_id != 0x0400:
            raise Exception("Invalid device ID!", device_id)

            # print("MCP9808 initialized!")

    def i2c_read_16(self, register):
        raw_bytes = self.i2c_ref.mem_read(2, self.addr, register)
        return struct.unpack(">h", raw_bytes)[0]

    def get_raw(self):
        return self.i2c_read_16(self.AMBIENT_TEMP)

    def read(self):
        raw = self.get_raw()

        temperature = raw & 0x0fff
        temperature /= 16.0
        if raw & 0x1000:
            temperature -= 0x100

        return temperature

    def update_data(self):
        self.data[0] = self.get_raw()


class TMP36(Sensor):
    def __init__(self, sensor_id, adc_pin, vcc=3.3):
        super().__init__(sensor_id, 'u16')

        self.pin_ref = pyb.ADC(pyb.Pin(adc_pin, pyb.Pin.ANALOG))
        self.vcc = vcc * 1000

    def read(self):
        raw = self.pin_ref.read()
        millivolts = self.vcc / 1024 * raw
        return (millivolts - 500) / 100

    def update_data(self):
        self.data[0] = self.pin_ref.read()


class BuiltInAccel(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i8', 'i8', 'i8')

        self.accel = pyb.Accel()

    def update_data(self):
        self.data = (self.accel.x(), self.accel.y(), self.accel.z())


class GPS(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i16', 'f', 'i16', 'f', 'f', 'f', 'f')

        self.gps_ref = MicropyGPS()

    def update(self, character):
        self.gps_ref.update(character)

    def update_data(self):
        self.data = \
            (self.gps_ref.latitude[0],
             self.gps_ref.latitude[1],
             self.gps_ref.longitude[0],
             self.gps_ref.longitude[1],

             self.gps_ref.speed[2],
             self.gps_ref.hdop,
             self.gps_ref.course)


class Servo(Command):
    def __init__(self, command_id, pin_num):
        super().__init__(command_id, 'i8')
        
        self.servo_ref = pyb.Servo(pin_num)

    def callback(self, angle):
        self.servo_ref.angle(angle)


class Orientation(Sensor):
    def __init__(self, sensor_id, bus):
        super().__init__(sensor_id, 'f', 'f', 'f', 'f', 'f', 'f', 'f')
    
        self.accel = Accelerometer(bus)
        self.mag = Magnetometer(bus)
        self.gyro = Gyroscope(bus)
        self.bmp = Barometer(bus)

    def get_orientation(self):
        roll = math.atan2(self.accel.y,
                          self.accel.z)
        if (self.accel.y * math.sin(roll) +
                    self.accel.z * math.cos(roll) == 0):
            pitch = math.pi / 2 if self.accel.x > 0 else -math.pi / 2
        else:
            pitch = math.atan(-self.accel.x / self.accel.y * math.sin(roll) +
                              self.accel.y * math.cos(roll))

        heading = math.atan2(self.mag.z * math.sin(
                roll) - self.mag.y * math.cos(roll),
                             self.mag.x * math.cos(pitch) +
                             self.mag.y * math.sin(pitch) * math.sin(
                                     roll) +
                             self.mag.z * math.sin(pitch) * math.cos(
                                     (roll)))
        return roll, pitch, heading

    def update_data(self):
        self.accel.refresh()
        self.mag.refresh()

        roll, pitch, heading = self.get_orientation()

        self.bmp.refresh()
        self.gyro.refresh()

        self.data = (roll, pitch, heading, self.bmp.altitude,
                     self.gyro.v_x, self.gyro.v_y, self.gyro.v_z)


class Encoder(Sensor):
    def __init__(self, sensor_id, pin_x, pin_y, pin_mode=pyb.Pin.PULL_NONE,
                 scale=1, min=None, max=None, reverse=False):
        super().__init__(sensor_id, 'i64')
        
        self.encoder = Encoder(pin_x, pin_y, pin_mode, scale, min, max, reverse)
        
    def update_data(self):
        self.data = self.encoder.position



class Motor(Command):
    # pin name: [(timer #, channel #), ...]
    pin_channels = {
        'X1': [(2, 1), (5, 1)],
        'X2': [(2, 2), (5, 2)],
        'X3': [(2, 3), (5, 3), (9, 1)],
        'X4': [(2, 4), (5, 4), (9, 2)],
        'X6': [(2, 1), (8, 1)],
        'X7': [(13, 1)],
        'X8': [(1, 1), (8, 1), (14, 1)],
        'X9': [(4, 1)],
        'X10': [(4, 2)],
        'Y1': [(8, 1)],
        'Y2': [(8, 2)],
        'Y3': [(4, 3), (10, 1)],
        'Y4': [(4, 4), (11, 1)],
        'Y6': [(1, 1)],
        'Y7': [(1, 2), (8, 2), (12, 1)],
        'Y8': [(1, 3), (8, 3), (12, 2)],
        'Y9': [(2, 3)],
        'Y10': [(2, 4)],
        'Y11': [(1, 2), (8, 2)],
        'Y12': [(1, 3), (8, 3)]
    }

    def __init__(self, command_id, direction_pin, pwm_pin, min_speed=40, max_speed=100):
        self.enable_pin = pyb.Pin(direction_pin, mode=pyb.Pin.OUT_PP)
        self.timer, self.channel = self.init_timer_channel(pwm_pin, 100)

        self.current_speed = 0
        self.min_speed = min_speed
        self.max_speed = max_speed

        super().__init__(command_id, 'i8')

    def init_timer_channel(self, pwm_pin, frequency):
        if pwm_pin in self.pin_channels:
            timer_num, channel_num = self.pin_channels[pwm_pin][0]

            timer = pyb.Timer(timer_num, freq=frequency)
            channel = timer.channel(channel_num, pyb.Timer.PWM, pin=pyb.Pin(pwm_pin))

            return timer, channel
        else:
            raise Exception("Not valid pin: " + str(pwm_pin))

    def constrain_speed_abs(self, value):
        if value == 0:
            return value

        if abs(value) < self.min_speed:
            return self.min_speed

        if abs(value) > self.max_speed:
            return self.max_speed

        return abs(value)

    def speed(self, value=None):
        if value == None:
            return self.current_speed
        else:
            if value == 0:
                self.enable_pin.value(0)
                self.channel.pulse_width_percent(0)
            elif value < 0:
                self.enable_pin.value(1)
                self.channel.pulse_width_percent(
                    100 - self.constrain_speed_abs(value))
            else:
                self.enable_pin.value(0)
                self.channel.pulse_width_percent(
                    self.constrain_speed_abs(value))
            self.current_speed = value

