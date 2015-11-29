"""
    Written by Ben Warwick

    objects.py, written for RoboQuasar1.0
    Version 11/28/2015
    =========

    Object wrappers for sensors and commands
    Each sensor handles its own data interpretation.

    Usage
    -----

    # Collecting data:

    from board import comm
    from board.objects import *

    imu = IMU(0)
    gps = GPS(1)
    encoder = Encoder(2)

    servo = Servo(0)
    led13 = Led13(1)

    sensor_data = SensorData(imu=imu, gps=gps, encoder=encoder)
    command_queue = CommandQueue(servo=servo, led13=led13)

    communicator = comm.Communicator(115200, command_queue, sensor_data)
    communicator.start()

    try:
        while True:
            roll, pitch, yaw = imu.get_orientation()
            x, y = encoder.get_xy()

            print roll, pitch, yaw
            print gps.long, gps.lat
            print x, y
    except KeyboardInterrupt:
        comm.exit_flag = True

    # Making your own Sensor and Command subclass

    As mentioned in data.py, the serial protocol used sends data purely in hex.
    So, in order to interpret the data, you must supply information on how to
    interpret the data. This can be tricky. Each format produces an expected
    data length. If this does not match what's returned from the serial stream,
    the data will be ignored (a print statement will tell you so).

    There are 13 individual data types supported. Signed and unsigned variants
    of integer sizes (8, 16, 32, and 64), float, double, boolean, raw hex, and
    character.

    Each of these can be represented as a hexidecimal number which the packet
    protocol has taken advantage of. The IMU (inertial measurement unit) on the
    arduino we're using gives acceleration, gyroscope, and magnetometer
    (compass) data. Those three sensors have x, y, and z components. It returns
    each component as a signed 16-bit number.

    A packet from this sensor might look like this:

    00	c46f5983acd5a02aabf6e8cb5a68110a6014

    Garbage right? Well, not so fast. We know it returns 9 signed 8-bit numbers.
    A signed (as well as unsigned) 16-bit number takes up 4 hex character. This
    means every grouping of 4 hex character is a component of data.
    This data translates to this:
    -15249	22915	-21291	-24534	-21514	-5941	23144	4362	24596

    Much more readable! So, to create an IMU class, we need to tell the Sensor
    class we want 9 signed 16-bit numbers returns from our packet of data.
    So, in the __init__ method of your new class, call Sensor's construct:
    super(IMU, self).__init__(sensor_id,
                                  'i16', 'i16', 'i16',
                                  'i16', 'i16', 'i16',
                                  'i16', 'i16', 'i16')
    Note: 'i16' is equivalent to 'int16'

    What about the other data types? For the GPS, it returns 4 float numbers
    followed by two unsigned 8-bit numbers.
    To represent that, we give ('f', 'f', 'f', 'f', 'u8', 'u8') to Sensor's
    constructor. If you look at a GPS packet, its length is 36 since each float
    is 8 characters and an unsigned 8-bit is 2 (8 * 4 + 2 * 2 = 36).

    For Commands, the formatting is similar except floats and doubles are
    excluded because of the limitations of the arduino code we've written
    (we were too lazy to add floating point).

    For a servo Command, a call to the super class might look like this:

    super(Servo, self).__init__(command_id, 'u8')

    since servos typically only require an unsigned 8-bit of data.

    To experiment with the other data types, call data.experiment in a test
    file. Here's a mini reference for all the data types:

    'u8' = 'uint8': 2
    'u16' = 'uint16': 4
    'u32' = 'uint32': 8
    'u64' = 'uint64': 16

    'i8' = 'int8': 2
    'i16' = 'int16': 4
    'i32' = 'int32': 8
    'i64' = 'int64': 16

    'f' = 'float': 8
    'd' = 'double': 16
    'b' = 'bool: 1

    'h' = 'hex': None
    'c': 'chr': None

    You might notice hex and chr have lengths of None. This is because you can
    specify the length. hex does nothing to the data, but chr interprets the
    hex digits as ASCII characters (0x61 = 'a'). To specify the length for
    either of these types, put the data length after the format flag in decimal:

    super(ChrSensor, self).__init__(sensor_id, 'c10', 'u8')

    This sensor will now interpret the first 20 hex characters as a string
    (since characters require 2 hex digits).

    Dependencies
    ------------
    data.py
"""

import math
from data import Sensor
from data import Command


class IMU(Sensor):
    def __init__(self, sensor_id):
        super(IMU, self).__init__(sensor_id,
                                  'i16', 'i16', 'i16',
                                  'i16', 'i16', 'i16',
                                  'i16', 'i16', 'i16')

    @property
    def accel_x(self):
        return self.data[0]

    @property
    def accel_y(self):
        return self.data[1]

    @property
    def accel_z(self):
        return self.data[2]

    @property
    def gyro_x(self):
        return self.data[3]

    @property
    def gyro_y(self):
        return self.data[4]

    @property
    def gyro_z(self):
        return self.data[5]

    @property
    def magnet_x(self):
        return self.data[6]

    @property
    def magnet_y(self):
        return self.data[7]

    @property
    def magnet_z(self):
        return self.data[8]

    def get_orientation(self):
        roll = math.atan2(self.accel_y,
                          math.sqrt(self.accel_x ** 2 + self.accel_z ** 2))
        pitch = math.atan2(self.accel_x,
                           math.sqrt(self.accel_y ** 2 + self.accel_z ** 2))
        yaw = math.atan2(
            (-self.magnet_y * math.cos(roll) + self.magnet_z * math.sin(roll)),
            (self.magnet_x * math.cos(pitch) + self.magnet_y * math.sin(
                pitch) * math.sin(roll) + self.magnet_z * math.sin(
                pitch) * math.cos(roll)))

        return roll, pitch, yaw


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
    def __init__(self, sensor_id, initial_x=0, initial_y=0):
        self.prev_x, self.prev_y = initial_x, initial_y
        self.prev_dist = 0

        super(Encoder, self).__init__(sensor_id, 'u64')

    @property
    def distance(self):
        return self.data[0]

    def get_xy(self, yaw):
        dist_change = self.distance - self.prev_dist

        self.prev_x += math.cos(yaw) * dist_change
        self.prev_y += math.sin(yaw) * dist_change

        return self.prev_x, self.prev_y


class Servo(Command):
    def __init__(self, command_id):
        super(Servo, self).__init__(command_id, 'u8')

    @property
    def position(self):
        # if we get the analog feedback servo, change this class to use two
        # other classes: a command servo and a sensor servo
        return self.data


class Led13(Command):
    def __init__(self, command_id):
        super(Led13, self).__init__(command_id, 'b')

    @property
    def state(self):
        return self.data
