# A file we would run should go out to roll to collect data again
# (assuming we have the buggy remote controlled)

import sys
import math

sys.path.insert(0, '../')

from board import logger
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

log = logger.Recorder()

try:
    while True:
        print(imu.data)
        print(gps.data)
        print(encoder.data)

        log.add_data("imu", imu)
        log.add_data("gps", gps)
        log.add_data("encoder", encoder)

except KeyboardInterrupt:
    comm.exit_flag = True
