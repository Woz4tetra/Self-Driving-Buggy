
'''
This module contains methods and classes relating to interpreting data
about the buggy like position and orientation.
'''

import math

def convertToHeading(magnetX, magnetY, magnetZ):
    roll = math.atan2(magnetX, magnetZ)
    pitch = math.atan2(magnetY, magnetZ)
    yaw = math.atan2(magnetY, magnetX)

    if yaw < 0:
        yaw += 2 * math.pi

    return roll, pitch, yaw

def adjustForTilt(accelX, accelY, accelZ, roll, pitch, yaw):  # forward is x, sideways is y
    '''
    Uses 3D trig to adjust acceleration data for tilt. The reference frame is
    the gyroscope's initial orientation.

    :param accelX: float (m/s)
    :param accelY: float (m/s)
    :param accelZ: float (m/s)
    :param roll: float (radians)
    :param pitch: float (radians)
    :param yaw: float (radians)
    :return: a tuple of floats containing the new angle data
    '''
    return (accelX * math.cos(roll) * math.cos(yaw),
            accelY * math.cos(pitch) * math.cos(yaw),
            accelZ * math.cos(pitch) * math.cos(roll))

class Position(object):
    def __init__(self, initial, initialV=0, metersToIndex=1):
        '''
        This class double integrates acceleration data to get position using
         the Middle Riemann sum algorithm. Create multiple instances for
         multiple dimension:

        posX = buggyinfo.Position(0)
        posY = buggyinfo.Position(0)
        posZ = buggyinfo.Position(0)

        :param initial: a number specifying initial position
        :param initialV: a number specifying initial velocity
        :return: Instance of Position
        '''
        self.pos = initial

        self.veloc = [initialV]

        self.accel = []
        
        self.metersToIndex = metersToIndex

    def update(self, accel, dt):
        '''
        Update position using new acceleration data and dt.

        :param accel: a float (m/s)
        :param dt: time in milliseconds since last sample from IMU
        :return: None
        '''
        if len(self.accel) == 0:
            self.accel.append(accel)
        elif len(self.accel) == 1:
            velocX = self._integrate(self.veloc[0], accel, self.accel, dt)
            self.pos = self._integrate(self.pos, velocX, self.veloc, dt)
        elif len(self.accel) == 2:
            velocX = self._integrate(self.veloc[1], accel, self.accel, dt)
            self.pos = self._integrate(self.pos, velocX, self.veloc, dt)


    def _integrate(self, initial, current, avgList, dt):
        '''
        An internal method that integrates data using the Middle Riemann sum:
        https://en.wikipedia.org/wiki/Riemann_sum#Middle_sum

        :param initial: The initial value. Either velocity or acceleration
        :param current: Current velocity or acceleration
        :param avgList: The two values to average
        :param dt: time in milliseconds since last sample from IMU
        :return: The new integrated value
        '''
        avgList.append(current)
        if len(avgList) > 2:
            avgList.pop(0)

        average = sum(avgList) / len(avgList)

        return initial + average * dt
    
    def convert(self):
        return int(self.pos * self.metersToIndex)
    
    def __str__(self):
        return str(self.pos)

    def __float__(self):
        return float(self.pos)

    def __int__(self):
        return int(self.pos)

    def __eq__(self, other):
        if type(other) == int or type(other) == long or type(other) == float:
            return self.pos == other
        elif isinstance(other, self.__class__):
            return self.pos == other.pos
        else:
            return False


    # Tests:
    # posX = Data.position(0, 0)
    # posY = Data.position(0, 0)
    #
    # posX.update(0.01, 0.5)
    # posY.update(1.0, 0.5)
    #
    # time1 = time.time()
    # times = []
    # for _ in xrange(9999):
    #     time3 = time.time()
    #     posX.update(0.01, 0.5)
    #     posY.update(0.0, 0.5)
    #     time4 = time.time()
    #     times.append(time4 - time3)
    #
    # time2 = time.time()
    #
    # print time2 - time1, sum(times) / len(times)
    #
    # print (posX, posY)