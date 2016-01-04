# main.py -- put your code here!

import pyb
from pyb import UART
from objects import *
from data import *
from comm import Communicator

tmp36 = TMP36(0, pyb.Pin.board.Y12)
mcp9808 = MCP9808(1, 2)
accel = BuiltInAccel(2)
gps = GPS(3)
# orientation = Orientation(4, 1)

servo1 = Servo(0, 1)

new_data = False
def pps_callback(line):
    global new_data
    new_data = True

uart = UART(6, 9600, read_buf_len=1000)
pps_pin = pyb.Pin.board.X8
extint = pyb.ExtInt(pps_pin, pyb.ExtInt.IRQ_FALLING,
                    pyb.Pin.PULL_UP, pps_callback)

leds = []
for index in range(1, 5):
    pyb.LED(index).on()
    leds.append(pyb.LED(index))


sensor_queue = SensorQueue(tmp36,
                           mcp9808,
                           accel,
                           gps
                           )
command_pool = CommandPool(servo1)

communicator = Communicator(sensor_queue, command_pool)

toggle_index = 0
toggle_increase = True
time0 = pyb.millis()

while True:
    if new_data:
        while uart.any():
            gps.update(chr(uart.readchar()))
            
    new_data = False
    
    communicator.write_packet()
    communicator.read_command()
    
    if (pyb.millis() - time0) > 250:
        leds[toggle_index].off()
        if toggle_index == 3:
            toggle_increase = False
        elif toggle_index == 0:
            toggle_increase = True
        
        if toggle_increase:
            toggle_index += 1
        else:
            toggle_index -= 1
        leds[toggle_index].on()
        
        time0 = pyb.millis()

    pyb.delay(5)
