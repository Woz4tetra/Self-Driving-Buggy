
import pyb
from sensors import Sensor

class Communicator(object):
    def __init__(self):
        self.serial_ref = pyb.USB_VCP()
    
    def write_packet(self, sensor):
        assert(isinstance(sensor, Sensor))
        
        self.serial_ref.write(sensor.get_packet())
    
#    def read_command(self):
#        command = self.serial_ref.readline()
#        
#        command_id = int(command_id[0:2], 16)
#        data_len = int(command_id[3:5], 16)
#        data = 
    
    def close(self):
        self.serial_ref.close()
