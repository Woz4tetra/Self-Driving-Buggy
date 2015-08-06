import sys
# import time

import arduino
import buggyinfo
import numpy
from make_filter import *


def run():
    # Init arduino properties, drawer, and map
    # while exit is false:
    # get accel and gyro
    # smooth with kalman
    # get position
    # update map (any new blocked nodes? Use image processing, ultrasonic, and other sensors)
    # plot astar to end
    # plot smooth path through next four nodes, extract angles (bezier curve, if angle is greater than allowed turn radius, eliminate node from path, or if its another buggy, slow the hell down!!!)
    # command angles to arduino until next node appears

    IMU = arduino.IMU()

    posX = buggyinfo.Position(0)
    posY = buggyinfo.Position(0)
    posZ = buggyinfo.Position(0)

    # constants
    n_time_steps = 10000
    n_dim_state = 3
    filtered_state_means = np.zeros((n_time_steps, n_dim_state))
    filtered_state_covariances = np.zeros(
        (n_time_steps, n_dim_state, n_dim_state))

    kf = make_filter()
    t = 0

    while True:
        accel, gyro, magnet, dt = IMU.getIMU()  # get accel and gyro

        #if (t == 0):
        #    filtered_state_means[t] = numpy.array(
        #        [accel.x, accel.y, accel.z])
        #    filtered_state_covariances[t] = numpy.eye(n_dim_state)

        if t < 100:
            print t
            continue
        elif t == 100:
            filtered_state_means[t] = numpy.array(
                   [accel.x, accel.y, accel.z])
            filtered_state_covariances[t] = numpy.eye(n_dim_state)
        else:
            obs = numpy.array([accel.x, accel.y, accel.z])
            results = kf.filter_update(filtered_state_means[t],
                                       filtered_state_covariances[t], obs)
            filtered_state_means[t + 1], filtered_state_covariances[t + 1] = results

            x, y, z = filtered_state_means[t + 1]


            # get position
            posX.update(x, dt)
            posY.update(y, dt)
            posZ.update(z, dt)

            # magnet.roll, magnet.pitch, magnet.yaw = \
            #     buggyinfo.convertToHeading(magnet.x, magnet.y, magnet.z)
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (accel.x, accel.y, accel.z,
                                                          x, y, z, int(posX),
                                                          int(posY), int(posZ))
        t += 1

    arduino.arduino.stop()


if __name__ == '__main__':
    arguments = sys.argv
    if "help" in arguments or "h" in arguments:
        print NotImplementedError
    if "upload" in arguments:
        arduino.initBoard(upload=True)
    elif "load" in arguments:
        arduino.initBoard(uploadOnly=True)
    else:
        arduino.initBoard()

    run()
