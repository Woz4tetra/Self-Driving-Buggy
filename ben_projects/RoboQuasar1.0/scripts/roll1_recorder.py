# mimics the script run during RoboQuasar's first coursewalk

import sys
import math

sys.path.insert(0, '../')

from board import logger
import gc_joystick
from board import comm
from board.data import *

imu = Sensor(0, 'i16', 'i16', 'i16',
             'i16', 'i16', 'i16',
             'i16', 'i16', 'i16')
gps = Sensor(1, 'f', 'f', 'f', 'f', 'u8', 'u8')
encoder = Sensor(2, 'u64')

servo = Command(0, 'u8')
led13 = Command(1, 'b')

sensor_data = SensorData(imu=imu, gps=gps, encoder=encoder)
command_queue = CommandQueue(servo=servo, led13=led13)

communicator = comm.Communicator(115200, command_queue, sensor_data)
communicator.start()

servo_value = 0
led13_value = True

joystick = gc_joystick.init()

log = logger.Recorder()

def joystick_angle(position):
    if math.sqrt(position[0] ** 2 + position[1] ** 2) > 0.6:
        return -int(
            math.degrees(math.atan2(position[1], position[0])) * 125 / 180)
    else:
        return -1


try:
    while joystick.done is False:
        joystick.update()

        servo_value = joystick_angle(joystick.mainStick)

        print(imu.data)
        print(gps.data)
        print(encoder.data)

        log.add_data("imu", imu)
        log.add_data("gps", gps)
        log.add_data("encoder", encoder)

        if 0 <= servo_value <= 125:
            command_queue.put(servo, servo_value)
            # command_queue.put(led13, led13_value)

except KeyboardInterrupt:
    comm.exit_flag = True
