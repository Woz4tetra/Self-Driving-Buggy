
import pygame
from controllers.joystick import BuggyJoystick

def run():
    pygame.display.init()
    pygame.joystick.init()
    print "joysticks:", joysticks

    buggy_joystick = BuggyJoystick()

    done = False
    while done is False:
        buggy_joystick.update()


if __name__ == '__main__':
    print __doc__
    run()
