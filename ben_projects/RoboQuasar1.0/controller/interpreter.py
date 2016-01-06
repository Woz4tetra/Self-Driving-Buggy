"""
    Written by Jason Kagie (modified by Ben Warwick)

    interpreter.py, written for RoboQuasar1.0
    Version 1/4/2016
    =========

    Interprets sensor data from board/data.py to x, y, theta (current position).

    Classes:
        Filter - contains a kalman filter tailored for gps, encoder,
            accelerometer and orientation input
"""

import numpy as np
import pykalman
import math
import time


class Filter(object):
    def __init__(self, latitude, longitude):
        self.origin = latitude, longitude
        self.filt_state_mean = np.array(
                [0, 0, 0, 0, 0, 0])  # (x=0,y=0,vx=0,vy=0,ax=0,ay=0)
        self.filter = pykalman.KalmanFilter()
        self.covariance = np.identity(6)
        self.dt = time.time()

    def update(self, gps, encoder, accel, orientation) -> (float, float):
        """
        observation -> observation matrix:
            x,y,N,ax,ay to x,y,vx,vy,ax,ay - given an angle phi and change in time,
        encoder distance (N) can be converted to velocity.

        x_gps = x
        y_gps = y
        N = radius * time / cos(phi) * Vx (in other words Vx = N * cos(phi) / (radius*time))
        accel_x = Ax
        accel_y = Ay


        observation matrix 1 -> observation matrix 2
        x,y,Vx,Vy,Ax,Ay to x,y,Vx,Vy,Ax,Ay - how does the error increase
        with time?
            A variance (how the data corrupts itself) of 1 means the
        data cannot be trusted until the next measurement. These are the
        diagonal values in the matrix. A variance that changes with time
        implies the measurement drifts with time.
            A covariance (how each sensor corrupts each other) of 0 implies
        the sensors do not disrupt each other.

        x'  = x  + time*Vx
        y'  = y  + time*Vy
        Vx' = Vx + time*Ax
        Vy' = Vy + time*Ay
        Ax' = Ax
        Ay' = Ay

        :param gps: board.xxx_objects.GPS - contains raw gps data
        :param encoder: board.xxx_objects.Encoder - contains encoder data
        :param accel: board.xxx_objects.Accelerometer - contains raw accel data
        :param orientation: board.xxx_objects.Orientation - contains heading data
        :return: current x, y as determined by the kalman filter
        """
        self.dt = time.time() - self.dt

        observation = np.array([gps.longitude, gps.latitude,
                                encoder.position, accel.x, accel.y])

        observation_matrix = np.array(
                [[1, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0],
                 [0, 0,
                  encoder.radius * self.dt / math.cos(orientation.heading),
                  0, 0, 0],
                 [0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 1]]
        )

        transition_matrix = np.array(
                [[1, 0, self.dt, 0, 0, 0],
                 [0, 1, 0, self.dt, 0, 0],
                 [0, 0, 1, 0, self.dt, 0],
                 [0, 0, 0, 1, 0, self.dt],
                 [0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 1]]
        )

        self.filt_state_mean, self.covariance = self.filter.filter_update(
                filtered_state_mean=self.filt_state_mean,
                filtered_state_covariance=self.covariance,
                observation=observation,
                transition_matrix=transition_matrix,
                observation_matrix=observation_matrix)

        return self.filt_state_mean[0], self.filt_state_mean[1]  # x, y
