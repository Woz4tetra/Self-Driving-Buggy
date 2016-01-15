import time
import traceback
import sys

sys.path.insert(0, '../')

from board import comm
from board import logger
from board.micropy_objects import *
from board.data import *
from controller.interpreter import MainFilter

builtin_accel = BuiltinAccel(2)
gps = GPS(3)
imu = MPU6050(4)
compass = HMC5883L(5)
encoder = ()

servo1 = Servo(0, -90)

sensor_data = SensorPool(
        builtin_accel,
        gps,
        imu,
        compass
)
command_queue = CommandQueue()

communicator = comm.Communicator(115200, command_queue, sensor_data,
                                 use_handshake=False)
communicator.start()

kalman_filter = MainFilter(gps.latitude, gps.longitude, 1, compass.heading)

servo_increase = True

log_data = False
log = None
if log_data:
    log = logger.Recorder()

    log.add_sensor(builtin_accel, 'builtin_accel', "accel x", "accel y",
                   "accel z")
    log.add_sensor(gps, 'gps', "lat deg", "long deg", "lat min", "long deg",
                   "speed", "hdop", "heading")
    log.add_sensor(servo1, 'servo1', "degrees")
    log.end_init()

time_stamp0 = 0

try:
    while True:
        # if servo_increase:
        #     servo1.offset(1)
        # else:
        #     servo1.offset(-1)
        #
        # if servo1.degrees == 90 or servo1.degrees == -90:
        #     servo_increase = not servo_increase
        #
        # command_queue.put(servo1)

        time.sleep(0.005)

        # print(builtin_accel)
        # print(gps)
        # print(servo1)
        # print(imu)
        # print(compass)
        kalman_filter.update(gps, encoder, imu, compass)

        if log_data:
            time_stamp1 = int(time.time() - log.time0)
            if time_stamp1 != time_stamp0:
                time_stamp0 = time_stamp1
                log.add_data(builtin_accel)
                log.add_data(gps)
                log.add_data(servo1)
                log.end_row()
except:
    if log_data:
        log.close()
    traceback.print_exc()
    comm.exit_flag = True
