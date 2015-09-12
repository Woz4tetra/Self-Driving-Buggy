# main.py -- put your code here!
# Chris's Servo Test program

import pyb
import time
pyb.LED(4).on()

servo1 = pyb.Servo(1)
servo1.angle(0)


while True:
    servo1.angle(-90,1000)
    time.sleep(1)
    servo1.angle(90,1000)
    time.sleep(1)


"""
from stepper_motor import *
import pyb

motor = Stepper(['X2', 'X3', 'X4', 'X5'])
LEDs = []

for index in [1, 2, 3, 4]:
    LEDs.append(pyb.LED(index))

counter = 0
for _ in range(2000):
    motor.do_step()

    LEDs[counter].toggle()
    pyb.delay(100)

    counter += 1
    if counter >= 4:
        counter = 0
"""
