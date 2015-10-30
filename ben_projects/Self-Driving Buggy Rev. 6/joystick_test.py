
import pygame

import config  # put this before local module imports

from controllers.joystick import BuggyJoystick
from controllers.user_objects import *

def run():
    pygame.display.init()
    pygame.joystick.init()

    buggy_joystick = BuggyJoystick()
    buggy_joystick.deadzoneStick = 0

    while buggy_joystick.done is False:
        buggy_joystick.update()

        servo.set(
            (buggy_joystick.mainStick[0] + 0.71716998809778) * 160 / 1.5209)
        led13.set(buggy_joystick.buttons['A'])


if __name__ == '__main__':
    imu = AccelGyro()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=180)
    led13 = Led13()

    initialize(False)

    print __doc__
    run()
