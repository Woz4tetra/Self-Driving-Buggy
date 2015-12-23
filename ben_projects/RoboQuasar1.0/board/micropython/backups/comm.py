
import pyb
from objects import *

class Communicator(object):
    def __init__(self, sensor_queue, command_pool):
        self.serial_ref = pyb.USB_VCP()
        
        self.switch = pyb.Switch()
        self.switch.callback(self.handshake)
        
        self.sensor_queue = sensor_queue
        self.command_pool = command_pool
    
    def handshake(self):
        self.serial_ref.write("R")
        while not self.serial_ref.any():
            for index in range(1, 5):
                pyb.LED(index).toggle()
    
    def write_packet(self):
        self.serial_ref.write(self.sensor_queue.get())
    
    def read_command(self):
        if self.serial_ref.any():
            packet = self.serial_ref.readline().decode("utf-8")
            
            if type(packet) == str:
                self.command_pool.update(packet)
    
    def close(self):
        self.serial_ref.close()
