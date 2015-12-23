
import pyb
from pyb import I2C

from data import *

class MCP9808(Sensor):
    CONFIG            = 0x01
    CONFIG_SHUTDOWN   = 0x0100
    CONFIG_CRITLOCKED = 0x0080
    CONFIG_WINLOCKED  = 0x0040
    CONFIG_INTCLR     = 0x0020
    CONFIG_ALERTSTAT  = 0x0010
    CONFIG_ALERTCTRL  = 0x0008
    CONFIG_ALERTSEL   = 0x0004
    CONFIG_ALERTPOL   = 0x0002
    CONFIG_ALERTMODE  = 0x0001
    UPPER_TEMP        = 0x02
    LOWER_TEMP        = 0x03
    CRIT_TEMP         = 0x04
    AMBIENT_TEMP      = 0x05
    MANUF_ID          = 0x06
    DEVICE_ID         = 0x07
    
    def __init__(self, sensor_id, bus, addr=0x18):
        super().__init__(sensor_id, 'i16')
        self.bus = bus
        self.addr = addr
        
        self.i2c_ref = I2C(self.bus, I2C.MASTER)
        
        addresses = self.i2c_ref.scan()
        print("Scanning devices:", [hex(x) for x in addresses])
        if self.addr not in addresses:
            raise Exception("MCP9808 is not detected")
        
        manuf_id = self.i2c_read_16(self.MANUF_ID)
        if manuf_id != 0x0054:
            raise Exception("Invalid manufacture ID!", manuf_id)
        
        device_id = self.i2c_read_16(self.DEVICE_ID)
        if device_id != 0x0400:
            raise Exception("Invalid device ID!", device_id)
        
        # print("MCP9808 initialized!")
    
    def i2c_read_16(self, register):
        raw_bytes = self.i2c_ref.mem_read(2, self.addr, register)
        return struct.unpack(">h", raw_bytes)[0]
    
    def get_raw(self):
        return self.i2c_read_16(self.AMBIENT_TEMP)
    
    def read(self):
        raw = self.get_raw()
        
        temperature = raw & 0x0fff
        temperature /= 16.0
        if raw & 0x1000:
            temperature -= 0x100
        
        return temperature
    
    def get_packet(self):
        self.data = self.get_raw()
        
        return "%s\t%s\r" % (self.to_hex(self.object_id, 2),
                             self.to_hex(self.data, self.data_len))
    

class TMP36(Sensor):
    def __init__(self, sensor_id, adc_pin, vcc=3.3):
        super().__init__(sensor_id, 'u16')
        
        self.pin_ref = pyb.ADC(pyb.Pin(adc_pin, pyb.Pin.ANALOG))
        self.vcc = vcc * 1000
    
    def read(self):
        raw = self.pin_ref.read()
        millivolts = self.vcc / 1024 * raw
        return (millivolts - 500) / 100
    
    def get_packet(self):
        self.data = self.pin_ref.read()
        
        return "%s\t%s\r" % (self.to_hex(self.object_id, 2),
                             self.to_hex(self.data, self.data_len))

class BuiltInAccel(Sensor):
    def __init__(self, sensor_id):
        super().__init__(sensor_id, 'i8', 'i8', 'i8')
        
        self.accel = pyb.Accel()
    
    def get_packet(self):
        self.data = "%s%s%s" % (self.to_hex(self.accel.x(), 2),
                                self.to_hex(self.accel.y(), 2),
                                self.to_hex(self.accel.z(), 2))
        return "%s\t%s\r" % (self.to_hex(self.object_id, 2),
                             self.data)

class Servo(Command):
    def __init__(self, command_id, pin_num):
        self.servo_ref = pyb.Servo(pin_num)
        
        super().__init__(command_id, 'i8')
    
    def callback(self, angle):
        self.servo_ref.angle(angle)


