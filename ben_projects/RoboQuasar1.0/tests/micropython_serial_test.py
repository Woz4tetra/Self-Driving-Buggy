
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

sensor_data = SensorData(tmp36, mcp9808, builtin_accel)
command_queue = CommandQueue()

communicator = comm.Communicator(115200, command_queue, sensor_data)
communicator.start()

log_data = False
if log_data:
    log = logger.Recorder()

try:
    while True:
        if tmp36.data != None:
            millivolts = 3300.0 / 1024 * tmp36.data
            print (millivolts - 500) / 100
        
        if mcp9808.data != None:
            temperature = mcp9808.data & 0x0fff
            temperature /= 16.0
            if mcp9808.data & 0x1000:
                temperature -= 0x100
            print(temperature)
        
        if builtin_accel.data != None:
            print builtin_accel.data
        
        time.sleep(0.25)

#        if log_data:

except:
    traceback.print_exc()
    comm.exit_flag = True