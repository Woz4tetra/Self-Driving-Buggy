
import time
import traceback
import sys

sys.path.insert(0, '../')

from board import comm
from board import logger
from board.data import *

tmp36 = Sensor(0, 'u16')
mcp9808 = Sensor(1, 'i16')
builtin_accel = Sensor(2, 'i8', 'i8', 'i8')
gps = Sensor(3, 'i16', 'f', 'i16', 'f', 'f', 'f', 'f')

servo1 = Command(0, 'i8')
servo1_val = -90

sensor_data = SensorPool(tmp36, mcp9808, builtin_accel, gps)
command_queue = CommandQueue()

communicator = comm.Communicator(115200, command_queue, sensor_data, use_handshake=False)
communicator.start()

log_data = False
if log_data:
    log = logger.Recorder()

def servo_bound(value):
    while value < -90:
        value += 90
    while value > 90:
        value -= 90
    return value

try:
    while True:
        millivolts = 3300.0 / 1024 * tmp36.data
        print((millivolts - 500) / 100)
        
        temperature = mcp9808.data & 0x0fff
        temperature /= 16.0
        if mcp9808.data & 0x1000:
            temperature -= 0x100
        print(temperature)
        
        print(builtin_accel.data)
        
        print(gps.data)
        servo1_val = servo_bound(servo1_val + 5)
        servo1.data = servo1_val

        command_queue.put(servo1)
        
        time.sleep(0.005)

#        if log_data:
#             log data
except:
    traceback.print_exc()
    comm.exit_flag = True
