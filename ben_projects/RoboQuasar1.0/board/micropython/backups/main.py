# main.py -- put your code here!

import pyb
from objects import *
from data import *
from comm import Communicator

tmp36 = TMP36(0, pyb.Pin.board.Y12)
mcp9808 = MCP9808(1, 1)
accel = BuiltInAccel(2)

servo1 = Servo(0, 1)

#leds = [pyb.LED(index) for index in range(1, 5)]

sensor_queue = SensorQueue(tmp36, mcp9808, accel)
command_pool = CommandPool(servo1)

communicator = Communicator(sensor_queue, command_pool)

#toggle_index = 0
#servo_val = -90

while True:
    
#    print(tmp36.read(), mcp9808.read())
#    print(accel.x(), accel.y(), accel.z())
#    print(switch())
    
    communicator.write_packet()
    communicator.read_command()
    
#    leds[toggle_index].toggle()
#    toggle_index = (toggle_index + 1) % 4
    
#    servo1.angle(servo_val)
#    servo_val += 5
#    
#    if servo_val > 90:
#        servo_val = -90
    
    pyb.delay(50)

