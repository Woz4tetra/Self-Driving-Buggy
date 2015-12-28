
import time
import traceback
import sys

sys.path.insert(0, '../')

from board import comm
from board import logger
from board.data import *

imu = Sensor(0, 'i16', 'i16', 'i16',
                'i16', 'i16', 'i16',
                'i16', 'i16', 'i16')
gps = Sensor(1, 'f', 'f', 'f', 'f', 'u8', 'u8')
encoder = Sensor(2, 'u64')

servo = Command(0, 'u8')
led13 = Command(1, 'b')

sensor_data = SensorPool(imu, gps, encoder)
command_queue = CommandQueue()

communicator = comm.Communicator(115200, command_queue, sensor_data)
communicator.start()

servo_value = 0
led13_value = True

log_data = False
if log_data:
    log = logger.Recorder()

try:
    while True:
        print((imu.data))
        print((gps.data))
        print((encoder.data))
        print()

        time.sleep(0.25)

        command_queue.put(servo, servo_value)
        command_queue.put(led13, led13_value)

        if log_data:
            log.add_data("imu", imu)
            log.add_data("gps", gps)
            log.add_data("encoder", encoder)
            log.add_data("servo", servo)
            log.add_data("led13", led13)

        if servo_value == 0:
            servo_value = 156
        else:
            servo_value = 0

        led13_value = not led13_value

        time.sleep(0.25)
except:
    traceback.print_exc()
    comm.exit_flag = True