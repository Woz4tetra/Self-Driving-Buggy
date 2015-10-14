from board.wrapper import get_gps
from board.wrapper import get_encoder
from board.wrapper import get_imu

from map import map_maker

import math


class Binder:
    def __init__(self):
        self.longitude, self.latitude, gps_speed, \
            gps_angle, satellites, fix_quality = get_gps()
        
        self.position = [self.longitude, self.latitude]

        self.gyroYaw = 0
        self.encoderCounts0 = 0

        self.prevBind = [self.longitude, self.latitude]
        self.map = map_maker.get_map()

    def _update(self):
        # accel_x, accel_y, accel_z, \
        #     self.gyroYaw, gyro_pitch, gyro_roll = get_imu()
        # self.encoderCounts1 = get_encoder()
        # self.longitude, self.latitude, gps_speed, \
        #     gps_angle, satellites, fix_quality = get_gps()
        #
        # self.position[0] += math.cos(self.gyroYaw) * (
        #     self.encoderCounts1 - self.encoderCounts0)
        # self.position[1] += math.sin(self.gyroYaw) * (
        #     self.encoderCounts1 - self.encoderCounts0)
        # self.encoderCounts0 = self.encoderCounts1

        # If encoder calculated position is outside of gps error (2 meters?)
        # reset it to gps values

        pass

    def bind(self):
        self._update()

        return self.prevBind
    