import numpy as np
import pylab as pl
import time
import random
from pykalman import KalmanFilter


def make_filter():
    print "a"
    transition_matrix = np.ones((3, 3))
    transition_offset = [0, 0, 0]
    observation_matrix = np.eye(3)
    observation_offset = [0, 0, 0]
    transition_covariance = np.eye(3)
    observation_covariance = np.eye(3)
    initial_state_mean = [-50, -50, -50]
    initial_state_covariance = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    kf = KalmanFilter(
        transition_matrix, observation_matrix, transition_covariance,
        observation_covariance, transition_offset, observation_offset,
        initial_state_mean, initial_state_covariance,
        random_state=0
    )
    return kf


def test():
    kf2 = make_filter()
    data = np.asarray([[1, 0], [0, 0]])
    (means, covariances) = kf2.filter(data)
    print means, "means"
    print covariances, "covariances"
    data2 = np.asarray([[0, 1]])
    menas, covariances = kf2.filter_update(means, covariances, data2)
    print means

    kf = make_filter()
    data1 = np.eye(2) * 5
    print data1
    data2 = np.eye(2) * 6
    data3 = np.eye(2) * 5
    dataA = np.array(data1)
    data = np.array(data1)
    data_final = np.array([5, 5])
    filt_state_means, filt_state_covariances = kf.filter(data_final)
    print kf.filter_update(filt_state_means, filt_state_covariances,
                           observation=data)

# test()
# this test is now wrong after switching n_dim_states to 3
    
    
