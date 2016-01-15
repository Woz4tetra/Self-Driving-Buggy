
import time

from data import Sensor
from data import Command

imu = Sensor(0, ['accel.x', 'accel.y', 'accel.z',
                      'gyro.x', 'gyro.y', 'gyro.z',
                      'mag.x', 'mag.y', 'mag.z'])  # data type is specified by incoming packet
builtin_accel = Sensor(1)
encoder = Sensor(2, ['distance', 'delta'])

servo_steering = Command(0, ['position', 'speed'])
servo_brakes = Command(1)
motor = Command(2, 'speed')

while True:
    print(imu.accel.x, imu.accel.y, imu.accel.z)
    print(imu.gyro)
    print(imu.mag)

    print(builtin_accel[0], builtin_accel[1], builtin_accel[2])

    if servo_steering.position == 90:
        servo_steering.speed = -1
    if servo_steering.position == -90:
        servo_steering.speed = 1

    motor.speed = servo_steering.position + 90

    servo_brakes.data = servo_steering.position
    
    time.sleep(0.005)

# -------- micropython implementation (the hard part) ----------

import pyb
import I2Csensor

class Accelerometer(Sensor):
    address = 0x10

    def __init__(self, sensor_id, bus):
        super().__init__(sensor_id, ['f', 'f', 'f',
                                     'f', 'f', 'f',
                                     'f', 'f', 'f'])

        self.i2c = I2Csensor(bus, self.address)

    def update_data(self):
        pass  # do some i2c shit


