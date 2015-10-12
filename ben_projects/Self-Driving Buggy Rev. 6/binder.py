from board.wrapper import get_gps
from board.wrapper import get_encoder
from board.wrapper import get_imu

import math


class Binder:
    def __init__(self):
        self.longitude, self.latitude, gps_speed, \
            gps_angle, satellites, fix_quality = get_gps()
        self.encoder_position = [self.longitude, self.latitude]

        self.gyro_yaw = 0
        self.encoder_counts0 = 0

        self.prev_bind = [self.longitude, self.latitude]

    def _update(self):
        accel_x, accel_y, accel_z, \
            self.gyro_yaw, gyro_pitch, gyro_roll = get_imu()
        self.encoder_counts1 = get_encoder()
        self.longitude, self.latitude, gps_speed, \
            gps_angle, satellites, fix_quality = get_gps()

        self.encoder_position[0] += math.cos(self.gyro_yaw) * (
            self.encoder_counts1 - self.encoder_counts0)
        self.encoder_position[1] += math.sin(self.gyro_yaw) * (
            self.encoder_counts1 - self.encoder_counts0)
        self.encoder_counts0 = self.encoder_counts1

    def bind(self):
        self._update()

        return # current bind
