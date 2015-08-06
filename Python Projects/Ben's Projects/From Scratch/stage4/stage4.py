import arduino
import time

board = arduino.Board("Board/stage4")

flags = {
    'time': 't',
    'add to var1': 'v',
    'print var1': 'p',
    'ultrasonic': 'u',
}

while True:
    board.write(flags['time'])
    print("".join(board.readUntil()))

    time.sleep(0.5)

    board.write(flags['add to var1'])
    board.write(flags['print var1'])

    print("".join(board.readUntil()))

    time.sleep(0.5)

    board.write(flags['ultrasonic'])
    print("".join(board.readUntil()))

    time.sleep(0.5)