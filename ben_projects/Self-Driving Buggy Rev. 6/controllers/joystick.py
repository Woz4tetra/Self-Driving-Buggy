import pygame

class BuggyJoystick:
    def __init__(self):
        self.deadzoneStick = 0.1
        self.mainStick = [0, 0]
        self.cStick = [0, 0]
        self.triggers = [0, 0]
        
        buttons = {
            "A": False,
            "B": False,
            "X": False,
            "Y": False,
            "Z": False,
            "L": False,
            "R": False,
            "start": False,
        }
        
        dpad = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }
        
        joysticks = [pygame.joystick.Joystick(x) for x in
                     xrange(pygame.joystick.get_count())]
        for joy in joysticks:
                 joy.init()
                 print joy.get_name(), joy.get_id(), joy.get_init(), joy.get_numaxes()
    
    def update(self):
        event = pygame.event.send()
        if event.type == pygame.QUIT:
            done = True
            break

        if event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > self.deadzoneStick and event.axis <= 3:
                if event.axis == 0:
                    self.mainStick[0] = event.value
                    print "main:", mainStick
                elif event.axis == 1:
                    self.mainStick[1] = event.value
                    print "main:", mainStick
                elif event.axis == 2:
                    self.cStick[0] = event.value
                    print "c:", cStick
                elif event.axis == 3:
                    self.cStick[1] = event.value
                    print "c:", cStick
            else:
                if event.axis == 4:
                    self.triggers[0] = event.value
                    print "L:", self.triggers[0]
                elif event.axis == 5:
                    self.triggers[1] = event.value
                    print "R:", self.triggers[1]
        elif event.type == pygame.JOYBUTTONDOWN:
            self._updateButtons(True)

        elif event.type == pygame.JOYBUTTONUP:
            self._updateButtons(False)

        elif event.type == pygame.JOYHATMOTION:
            print event.value

        elif event.type != pygame.NOEVENT:
            print event

    
    def _updateButtons(self, value):
        if event.button == 0:
            self.buttons["X"] = value
            print "X:", event
        elif event.button == 1:
            self.buttons["A"] = value
            print "A:", event
        elif event.button == 2:
            self.buttons["B"] = value
            print "B:", event
        elif event.button == 3:
            self.buttons["Y"] = value
            print "Y:", event
        elif event.button == 4:
            self.buttons["L"] = value
            print "L:", event
        elif event.button == 5:
            self.buttons["R"] = value
            print "R:", event
        elif event.button == 7:
            self.buttons["Z"] = value
            print "Z:", event
        elif event.button == 9:
            self.buttons["start"] = value
            print "start:", event
    
#    def __str__(self):

