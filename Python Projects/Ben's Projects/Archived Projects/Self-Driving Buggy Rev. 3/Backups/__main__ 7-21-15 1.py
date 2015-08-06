import sys
# import time

import arduino
import buggyinfo
import draw
import mapmaker


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

    dcmotor = arduino.DCMotor(1)
    IMU = arduino.IMU()
    button1 = arduino.Button(3)
    sonar1 = arduino.Sonar(1)
    stepper = arduino.Stepper(1)

    # grid, start, end = mapmaker.read()
    grid, start, end = mapmaker.make(30, 30), (0, 0), (5, 5)
    height, width = grid.shape[0:2]

    posX = buggyinfo.Position(start[0])
    posY = buggyinfo.Position(start[1])
    posZ = buggyinfo.Position(0)

    drawer = draw.Drawer(width, height, 700, 700, start, end, grid)

    dcmotor.forward(100)
    # stepper.forward(5)
    stepper.drive(10)

    while drawer.done is False:
        # time0 = time.time()
        accel, gyro, magnet, dt = IMU.getIMU()  # get accel and gyro

        # get position
        posX.update(accel.x, dt)
        posY.update(accel.y, dt)
        posZ.update(accel.z, dt)

        magnet.roll, magnet.pitch, magnet.yaw = \
            buggyinfo.convertToHeading(magnet.x, magnet.y, magnet.z)

        # print "(%0.3f, %0.3f, %0.3f)\t(%0.3f, %0.3f, %0.3f)" % \
        #       (gyro.roll, gyro.pitch, gyro.yaw,
        #        magnet.roll, magnet.pitch, magnet.yaw)
        # print "%s\t%s\t%s" % (accel.x, accel.y, accel.z)
        # print(sonar1.getDistance())

        if button1.wasPressed():
            dcmotor.reverse()

        # update map (any new blocked nodes? Use image processing, ultrasonic, and other sensors)
        # ignore until below routines are finished

        # plot astar to end
        # path, pathInfo, plotTime = astar.search(grid, (posX, posY), end)

        # plot smooth path through next four nodes, extract angles


        # command angles to arduino until next node appears
        drawer.loop()
        drawer.drawParticle(int(posX), int(posY))
        drawer.update()

        # print time.time() - time0

    drawer.deinit()
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
