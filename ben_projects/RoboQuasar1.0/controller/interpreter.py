# interprets sensor data from board/data.py to x, y, theta (current position)

import numpy as np
import pykalman
from math import *


class Filter(object):
    def __init__(self, latitude, longitude, radius):
        self.radius = radius
        self.conversion_factor = 1
        self.displacement_angle = 1
        self.origin = [latitude, longitude]
        self.filt_state_mean = np.array([0, 0, pi / 2, 0, 0, 0])
        self.filter = pykalman.KalmanFilter()
        self.covariance = np.identity(6)
        self.observation_matrix = np.array([])
        self.transition_matrix = np.array([])

    def update(self, angle, latitude, longitude, num_traveled,
               accel_x, accel_y, time):
        phi = np.arctan2((angle[0] * angle[2] + angle[1] * angle[3]),
                         (angle[1] * angle[2] - angle[0] * angle[3]))

        # print(phi, "azimuth")

        dlat = latitude - self.origin[0]
        dlong = longitude - self.origin[1]
        # TODO: why aren't these variables used?

        x_gps = (latitude - self.origin[0]) * self.conversion_factor
        y_gps = (longitude - self.origin[1]) * self.conversion_factor

        observation = np.array([x_gps, y_gps, num_traveled, accel_x, accel_y])
        # TODO: what is num_traveled?

        # x,y,N,ax,ay to x,y,vx,vy,ax,ay
        self.observation_matrix = np.array(
                [[1, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0],
                 [0, 0, self.radius * time / cos(phi), 0, 0, 0],
                 [0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 1]])
        # x,y,Vx,Vy,Ax,Ay 1 to x,y,Vx,Vy,Ax,Ay 2
        self.transition_matrix = np.array([[1, 0, time, 0, 0, 0],
                                           [0, 1, 0, time, 0, 0],
                                           [0, 0, 1, 0, time, 0],
                                           [0, 0, 0, 1, 0, time],
                                           [0, 0, 0, 0, 1, 0],
                                           [0, 0, 0, 0, 0, 1]])
        # TODO: check: 0, (covariance) measurements don't corrupt each other
        # TODO: check: 1, (variance) measurements are imperfect.
        #              will have vary these with experience

        next_mean, next_covariance = self.filter.filter_update(
                filtered_state_mean=self.filt_state_mean,
                filtered_state_covariance=self.covariance,
                observation=observation,
                transition_matrix=self.transition_matrix,
                observation_matrix=self.observation_matrix)

        self.filt_state_mean = next_mean
        self.covariance = next_covariance

        return next_mean[0], next_mean[1]
