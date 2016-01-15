"""
Allows for out-of-the-box interface with a gamecube controller (connected with
the mayflash gc adapter)

mainStick.x: -0.85...0.81 (left is negative)
mainStick.y: -0.82...0.80 (up is negative)

cStick.x: -0.76...0.70
cStick.y: -0.70...0.796

L: -0.777...0.84 (negative is up)
R: -0.809...0.809
"""

import pygame
from dotable import Dotable


class BuggyJoystick:
    # TODO: add multiple joystick support
    def __init__(self):
        self.deadzoneStick = 0.15
        self.mainStick = Dotable({
            'x': 0,
            'y': 0
        })
        self.cStick = Dotable({
            'x': 0,
            'y': 0
        })
        self.triggers = Dotable({
            'L': 0,
            'R': 0
        })

        self.buttons = Dotable({
            "A": False,
            "B": False,
            "X": False,
            "Y": False,
            "Z": False,
            "L": False,
            "R": False,
            "start": False,
        })

        self.dpad = Dotable({
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        })
        self.done = False

        joysticks = [pygame.joystick.Joystick(x) for x in
                     range(pygame.joystick.get_count())]
        for joy in joysticks:
            joy.init()
            print(joy.get_name(), joy.get_id(), joy.get_init(),
                  joy.get_numaxes())


    def update(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.done = True

        if event.type == pygame.JOYAXISMOTION:
            if event.axis <= 3:
                if event.axis == 0:
                    self.mainStick.x = event.value
                elif event.axis == 1:
                    self.mainStick.y = event.value
                elif event.axis == 2:
                    self.cStick.x = event.value
                elif event.axis == 3:
                    self.cStick.y = event.value
            else:
                if event.axis == 4:
                    self.triggers.L = event.value
                elif event.axis == 5:
                    self.triggers.R = event.value

            if (abs(self.mainStick.x) < self.deadzoneStick and
                        abs(self.mainStick.y) < self.deadzoneStick):
                self.mainStick.x = 0
                self.mainStick.y = 0
            if (abs(self.cStick.x) < self.deadzoneStick and
                        abs(self.cStick.y) < self.deadzoneStick):
                self.cStick.x = 0
                self.cStick.y = 0
        elif event.type == pygame.JOYBUTTONDOWN:
            self._updateButtons(event, True)

        elif event.type == pygame.JOYBUTTONUP:
            self._updateButtons(event, False)

        elif event.type == pygame.JOYHATMOTION:
            print(event.value)

            # elif event.type == pygame.NOEVENT:
            # if self.mainStick[0] < self.deadzoneStick:
            #     self.mainStick[0] = 0
            # if self.mainStick[1] < self.deadzoneStick:
            #     self.mainStick[1] = 0
            #
            # if self.cStick[0] < self.deadzoneStick:
            #     self.cStick[0] = 0
            # if self.cStick[1] < self.deadzoneStick:
            #     self.cStick[1] = 0

            # self.triggers[0] = 0
            # self.triggers[1] = 0

    def _updateButtons(self, event, value):
        if event.button == 0:
            self.buttons.X = value
        elif event.button == 1:
            self.buttons.A = value
        elif event.button == 2:
            self.buttons.B = value
        elif event.button == 3:
            self.buttons.Y = value
        elif event.button == 4:
            self.buttons.L = value
        elif event.button == 5:
            self.buttons.R = value
        elif event.button == 7:
            self.buttons.Z = value
        elif event.button == 9:
            self.buttons.start = value

    def __str__(self):
        return "x: %s, y: %s\n" \
               "cx: %s, cy: %s\n" \
               "A: %s, B: %s, X: %s, Y: %s\n" \
               "start: %s, Z: %s\n" \
               "L t: %s, R t: %s\n" \
               "left: %s, right: %s, up: %s, down: %s\n" \
               "L: %s, R: %s" % (
                   self.mainStick.x, self.mainStick.y,
                   self.cStick.x, self.cStick.y,
                   self.buttons.A, self.buttons.B, self.buttons.X,
                   self.buttons.Y, self.buttons.start, self.buttons.Z,
                   self.buttons.L, self.buttons.R,
                   self.dpad.left, self.dpad.right, self.dpad.up,
                   self.dpad.down,
                   self.triggers.L, self.triggers.R)


def init():
    pygame.display.init()
    pygame.joystick.init()

    return BuggyJoystick()


if __name__ == '__main__':
    import time

    joystick = init()
    while True:
        # print(joystick)
        joystick.update()

        time.sleep(0.005)
