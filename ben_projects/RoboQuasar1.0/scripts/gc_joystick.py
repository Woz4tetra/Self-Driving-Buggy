import pygame


class BuggyJoystick:
    def __init__(self):
        self.deadzoneStick = 0.15
        self.mainStick = [0, 0]
        self.cStick = [0, 0]
        self.triggers = [0, 0]

        self.buttons = {
            "A": False,
            "B": False,
            "X": False,
            "Y": False,
            "Z": False,
            "L": False,
            "R": False,
            "start": False,
        }

        self.dpad = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        self.done = False

        joysticks = [pygame.joystick.Joystick(x) for x in
                     xrange(pygame.joystick.get_count())]

        for joy in joysticks:
            joy.init()
            print joy.get_name(), joy.get_id(), joy.get_init(), joy.get_numaxes()

    def update(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.done = True

        if event.type == pygame.JOYAXISMOTION:
            if event.axis <= 3:
                if event.axis == 0:
                    self.mainStick[0] = event.value
                elif event.axis == 1:
                    self.mainStick[1] = event.value
                elif event.axis == 2:
                    self.cStick[0] = event.value
                elif event.axis == 3:
                    self.cStick[1] = event.value
            else:
                if event.axis == 4:
                    self.triggers[0] = event.value
                elif event.axis == 5:
                    self.triggers[1] = event.value

            if (abs(self.mainStick[0]) < self.deadzoneStick and
                        abs(self.mainStick[1]) < self.deadzoneStick):
                self.mainStick[0] = 0
                self.mainStick[1] = 0
            if (abs(self.cStick[0]) < self.deadzoneStick and
                        abs(self.cStick[1]) < self.deadzoneStick):
                self.cStick[0] = 0
                self.cStick[1] = 0
        elif event.type == pygame.JOYBUTTONDOWN:
            self._updateButtons(event, True)

        elif event.type == pygame.JOYBUTTONUP:
            self._updateButtons(event, False)

        elif event.type == pygame.JOYHATMOTION:
            print event.value

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
            self.buttons["X"] = value
        elif event.button == 1:
            self.buttons["A"] = value
        elif event.button == 2:
            self.buttons["B"] = value
        elif event.button == 3:
            self.buttons["Y"] = value
        elif event.button == 4:
            self.buttons["L"] = value
        elif event.button == 5:
            self.buttons["R"] = value
        elif event.button == 7:
            self.buttons["Z"] = value
        elif event.button == 9:
            self.buttons["start"] = value

if __name__ == '__main__':
    pygame.display.init()
    pygame.joystick.init()
    joystick = BuggyJoystick()

    # Do stuff with joystick
