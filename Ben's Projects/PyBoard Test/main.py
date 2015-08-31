# main.py -- put your code here!
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