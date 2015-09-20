
import time
import board
from board import devices

board.initBoard()

# servo1 = devices.Servo(1)
led1 = devices.BuiltInLED(1)

while True:
    led1.toggle()
    time.sleep(0.1)
    # if servo1.position == 90:
    #     servo1.position += 1
    # elif servo1.position == -90:
    #     servo1.position -= 1