import sys
import time
import arduino


def convertToBytes(data):
    bytes = [0, 0, 0]
    for index in xrange(3):
        bytes[index] = data % 0x100
        data /= 0x100
    return bytes


def writeSteps(goalStep):
    board.write('s')
    for index in xrange(2, -1, -1):
        board.write(chr(goalStep[index]))


if __name__ == '__main__':
    arguments = sys.argv
    if "stepper" in arguments:
        board = arduino.Board(disabled=False,
                              sketchDir="Uno Board Tests/Stepper Control")

        try:
            while True:
                goalStep = convertToBytes(int(raw_input("goal step: ")))
                writeSteps(goalStep)

                print "".join(board.readUntil()).split(',')

        except KeyboardInterrupt:
            pass
    elif "both" in arguments:
        board = arduino.Board(disabled=False,
                              sketchDir="Uno Board Tests/Stepper and IMU")
        try:
            while True:
                selector = raw_input("IMU (i) or stepper (s): ")
                goalStep = 0
                if selector == 's':
                    goalStep = convertToBytes(int(raw_input("goal step: ")))

                if selector == 's':
                    writeSteps(goalStep)
                else:
                    board.write(selector)
                print "".join(board.readUntil()).split(',')
        except KeyboardInterrupt:
            pass
    elif "oop1" in arguments:
        arduino.initBoard(disabled=False, sketchDir="Uno Board Tests/OOP Test")
        stepper = arduino.Stepper(1)
        IMU = arduino.IMU()

        try:
            while True:
                selector = raw_input("IMU (i) or stepper (s): ")
                if selector == 's':
                    subSelector = int(raw_input(
                        "0 = goal reached, 1 = move to, 2 = set speed\n selector: "))
                    if subSelector == 0:
                        print stepper.goalReached()
                    elif subSelector == 1:
                        goalStep = int(raw_input("goal step: "))
                        stepper.moveTo(goalStep)
                    elif subSelector == 2:
                        speed = int(raw_input("new speed: "))
                        stepper.setSpeed(speed)
                else:
                    print IMU.getData()

        except KeyboardInterrupt:
            pass
    elif "memory" in arguments:
        board = arduino.initBoard(disabled=False, sketchDir="Uno Board Tests/Free Memory Test")
        try:
            while True:
                board.write('b')
                time.sleep(0.001)
        except KeyboardInterrupt:
            pass


