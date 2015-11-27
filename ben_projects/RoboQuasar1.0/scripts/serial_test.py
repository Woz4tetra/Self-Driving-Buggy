
import time
import sys
sys.path.insert(0, '../')

from board import comm
from board.data import *

imu = Sensor(0, 'i8', 'i8', 'i8')
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

while True:
    print(imu.data)
    print(gps.data)
    print(encoder.data)

    time.sleep(0.25)

    command_queue.put(servo, servo_value)
    command_queue.put(led13, led13_value)

    if servo_value == 0:
        servo_value = 156
    else:
        servo_value = 0

    led13_value = not led13_value

    time.sleep(0.25)