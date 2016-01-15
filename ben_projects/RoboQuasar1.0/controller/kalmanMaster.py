import numpy as np
import pykalman
import time


class MainFilter(object):
    def __init__(self, latitude, longitude,circum, heading):
        self.headingKalman = headingKalman()
        self.placeKalman = placeKalman((latitude,longitude), circum, heading)
        self.time = time.time()
        self.dt = 0


    def update(self, gps, encoder, accel, phi, ang_accel):
        self.dt = time.time() - self.time
        self.time = time.time()
        phi = self.headingKalman.update(phi, ang_accel, self.dt)
        x,y = self.placeKalman.update(gps, encoder, accel, phi, self.dt)
        return (x, y, phi)

class headingKalman(object):
    def __init__(self):
        self.filter = pykalman.KalmanFilter()
        self.filt_state_mean = np.array([0.0,0.0]) # phi0 = 0, Vang0 = 0
        self.covariance = np.identity(2)
        self.obs_matrix = np.identity(2)
        
    def update(self, phi, Vang, dt):
        trans_matrix = np.array([[1,dt],
                                 [0,1]])
        obs = np.array([phi, Vang])
        self.filt_state_mean, self.covariance = self.filter.filter_update(
            filtered_state_mean = self.filt_state_mean,
            filtered_state_covariance = self.covariance,
            observation = obs,
            transition_matrix = trans_matrix,
            observation_matrix = self.obs_matrix)

        return self.filt_state_mean

class placeKalman(object):
    def __init__(self,origin, circum, start_heading):
        self.origin = origin
        self.circum = circum
        self.filt_state_mean = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.covariance = np.identity(6)
        self.displacement_angle = start_heading

    def update(self, gps, encoder, accel, phi, dt):
        (dist, x_gps, y_gps) = self.geo_dist(gps)
        observation = np.array([x_gps,y_gps,
                                encoder, accel[0], accel[1]])
        observation_matrix = np.array(
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 0.5*self.circum*dt/cos(phi),0.5*self.circum*dt/sin(phi),0,0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1])

        transition_matrix = np.array(
            [[1, 0, dt, 0, 0, 0],
            [0, 1, 0, dt, 0, 0],
            [0, 0, 1, 0, dt, 0],
            [0, 0, 0, 1, 0, dt],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1]]
        )

        self.filt_state_mean, self.covariance = self.filter.filter_update(
                filtered_state_mean=self.filt_state_mean,
                filtered_state_covariance=self.covariance,
                observation=observation,
                transition_matrix=transition_matrix,
                observation_matrix=observation_matrix)
        return self.filt_state_mean[0], self.filt_state_mean[1] # x, y

    def geo_dist(self,latitude, longitude):
        '''assuming the latitude and lontitude are given in degrees'''
        dLat  = latitude -  self.origin[0]
        dLong = longitude - self.origin[1]
        if dLat == 0:
            angle = 0
        else:
            angle = np.arctan(dLong/dLat)
        radius = 6378.137 #radius of Earth in km
        dLat  *= pi/180
        dLong *= pi/180
        a = (sin(dLat/2)  * sin(dLat/2)  +
             sin(dLong/2) * sin(dLong/2) * cos(self.origin[0]) * cos(self.origin[1]))
        c = 2 * np.arctan2(sqrt(a),sqrt(1-a))
        dist = radius * c * 1000
        dx = dist * cos(angle+self.displacement_angle)
        dy = dist * sin(angle+self.displacement_angle)
        return (dist, dx, dy)
