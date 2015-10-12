import pygame

pygame.display.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in
                xrange(pygame.joystick.get_count())]
print "joysticks:", joysticks

deadzone_stick = 0.1

mainStick = [0, 0]
cStick = [0, 0]

for joy in joysticks:
    joy.init()
    print joy.get_name(), joy.get_id(), joy.get_init(), joy.get_numaxes()

done = False
while done is False:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        done = True
        break

    if event.type == pygame.JOYAXISMOTION:
        if abs(event.value) > deadzone_stick and event.axis <= 3:
            if event.axis == 0:
                mainStick[0] = event.value
                print "main:", mainStick
            elif event.axis == 1:
                mainStick[1] = event.value
                print "main:", mainStick
            elif event.axis == 2:
                cStick[0] = event.value
                print "c:", cStick
            elif event.axis == 3:
                cStick[1] = event.value
                print "c:", cStick
        else:
            if event.axis == 4:
                print "L:", event.value
            elif event.axis == 5:
                print "R:", event.value
    elif event.type == pygame.JOYBUTTONDOWN:
        if event.button == 0:
            print "X:", event
        elif event.button == 1:
            print "A:", event
        elif event.button == 2:
            print "B:", event
        elif event.button == 3:
            print "Y:", event
        elif event.button == 4:
            print "L:", event
        elif event.button == 5:
            print "R:", event
        elif event.button == 7:
            print "Z:", event
        elif event.button == 9:
            print "start:", event

    elif event.type == pygame.JOYBUTTONUP:
        pass

    elif event.type == pygame.JOYHATMOTION:
        print event.value

    elif event.type != pygame.NOEVENT:
        print event
