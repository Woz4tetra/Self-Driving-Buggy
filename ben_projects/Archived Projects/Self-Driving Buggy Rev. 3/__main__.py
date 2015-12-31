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

    #threshhold
    th = 1

    while True:
        accel, gyro, magnet, dt = IMU.getIMU()  # get accel and gyro

        # if (t == 0):
        #    filtered_state_means[t] = numpy.array(
        #        [accel.x, accel.y, accel.z])
        #    filtered_state_covariances[t] = numpy.eye(n_dim_state)

        if t < 200:
            pass
        elif t == 200:
            filtered_state_means[t] = numpy.array(
                [accel.x, accel.y, accel.z])
            filtered_state_covariances[t] = numpy.eye(n_dim_state)
            print "passed"
        else:
            if abs(accel.x) < th:
                accel.x = 0
            if abs(accel.y) < th:
                accel.y = 0
            if abs(accel.z) < th:
                accel.z = 0
            obs = numpy.array([accel.x, accel.y, accel.z])
            results = kf.filter_update(filtered_state_means[t],
                                       filtered_state_covariances[t], obs,
                                       observation_offset = np.array([dt,dt,dt]))
            filtered_state_means[t + 1], filtered_state_covariances[
                t + 1] = results

            x, y, z = filtered_state_means[t + 1]

            if (abs(x - filtered_state_means[t][0]) > 3):
                x = 0
            if (abs(y - filtered_state_means[t][1]) > 3):
                y = 0
            if (abs(z - filtered_state_means[t][2]) > 3):
                z = 0

            if abs(x) < th:
                x = 0
            if abs(y) < th:
                y =0
            if abs(z) < th:
                z = 0


            # get position
            posX.update(x, dt)
            posY.update(y, dt)
            posZ.update(z, dt)

            # magnet.roll, magnet.pitch, magnet.yaw = \
            #     buggyinfo.convertToHeading(magnet.x, magnet.y, magnet.z)
            print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (
            accel.x, accel.y, accel.z,
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
