
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
