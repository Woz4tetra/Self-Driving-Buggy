# main.py -- put your code here!

from sensors import *
from comm import Communicator

tmp36 = TMP36(0, pyb.Pin.board.Y12)
mcp9808 = MCP9808(1, 1)

accel = pyb.Accel()

leds = [pyb.LED(index) for index in range(1, 5)]
servo1 = pyb.Servo(1)

switch = pyb.Switch()

sensor_pool = [tmp36, mcp9808]
sensor_index = 0

communicator = Communicator()

toggle_index = 0
servo_val = -90

while True:
    
#    print(tmp36.read(), mcp9808.read())
#    print(accel.x(), accel.y(), accel.z())
#    print(switch())
    
    communicator.write_packet(sensor_pool[sensor_index])
    sensor_index = (sensor_index + 1) % len(sensor_pool)
    
    leds[toggle_index].toggle()
    toggle_index = (toggle_index + 1) % 4
    
    servo1.angle(servo_val)
    servo_val += 5
    
    if servo_val > 90:
        servo_val = -90
    
    pyb.delay(50)

