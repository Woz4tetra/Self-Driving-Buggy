import time
import traceback
import sys

sys.path.insert(0, '../')

from board import comm
from board import logger
from board.micropy_objects import *
from board.data import *


tmp36 = TMP36(0)
mcp9808 = MCP9808(1)
builtin_accel = BuiltinAccel(2)
gps = GPS(3)

servo1 = Servo(0, -90)

sensor_data = SensorPool(tmp36, mcp9808, builtin_accel, gps)
command_queue = CommandQueue()

communicator = comm.Communicator(115200, command_queue, sensor_data,
                                 use_handshake=False)
communicator.start()

servo_increase = True

log_data = False
log = None
if log_data:
    log = logger.Recorder()

try:
    while True:
        print(tmp36.temperature)
        print(mcp9808.temperature)
        print(builtin_accel.x, builtin_accel.y, builtin_accel.z)
        print(gps.latitude, gps.longitude, gps.speed, gps.hdop, gps.heading)

        if servo_increase:
            servo1.offset(5)
        else:
            servo1.offset(-5)

        if servo1.degrees == 90 or servo1.degrees == -90:
            servo_increase = not servo_increase

        command_queue.put(servo1)

        time.sleep(0.005)

        if log_data:
            log.add_data('tmp36', tmp36)
            log.add_data('mcp9808', mcp9808)
            log.add_data('builtin_accel', builtin_accel)
            log.add_data('gps', gps)
            log.add_data('servo1', servo1)
except:
    traceback.print_exc()
    comm.exit_flag = True
