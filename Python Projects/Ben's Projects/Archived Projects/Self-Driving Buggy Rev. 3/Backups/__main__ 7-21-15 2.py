import sys
import time

import arduino
import draw
import mapmaker


def run():
    stepper = arduino.Stepper(1)

    # grid, start, end = mapmaker.read()
    # grid, start, end = mapmaker.make(30, 30), (0, 0), (5, 5)
    # height, width = grid.shape[0:2]

    # drawer = draw.Drawer(width, height, 700, 700, start, end, grid)

    # while drawer.done is False:
    while True:
        stepper.drive('forward', 255, 100)

        time.sleep(0.001)

        # drawer.loop()
        # drawer.update()

    # drawer.deinit()
    # arduino.arduino.stop()


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
