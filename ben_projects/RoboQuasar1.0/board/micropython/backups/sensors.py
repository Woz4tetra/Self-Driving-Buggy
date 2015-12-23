import pyb
from pyb import I2C

import struct
from sys import maxsize as MAXINT

class Sensor(object):
    short_formats = {
        'u8': 'uint8', 'u16': 'uint16', 'u32': 'uint32', 'u64': 'uint64',
        'i8': 'int8', 'i16': 'int16', 'i32': 'int32', 'i64': 'int64',
        'f': 'float', 'd': 'double',
        'b': 'bool',
        'h': 'hex', 'c': 'chr',
    }

    format_len = {
        'uint8': 2, 'uint16': 4, 'uint32': 8, 'uint64': 16,
        'int8': 2, 'int16': 4, 'int32': 8, 'int64': 16,
        'float': 8, 'double': 16,
        'bool': 1,
        'hex': None, 'chr': None,
    }
    
    def __init__(self, sensor_id, *formats):
        self.sensor_id = sensor_id
        self.data = 0
        
        self.formats = self.init_formats(list(formats))
        self.data_len = self.get_data_len(self.formats)
    
    def init_formats(self, formats):
        for index in range(len(formats)):
            if not self.is_format(formats[index]):
                raise Exception("Invalid format name: '%s'" % formats[index])

            if (formats[index] in self.short_formats and
                        self.get_len(formats[index]) == -1):
                formats[index] = self.short_formats[formats[index]]

        return formats
    
    def get_data_len(self, formats):
        data_len = 0
        for index in range(len(formats)):
            length = self.get_len(formats[index])
            if (length == -1):
                data_len += self.format_len[formats[index]]
            else:
                data_len += length

        return data_len
    
    def is_format(self, data_format):
        if data_format in self.short_formats.keys(): return True
        if data_format in self.format_len.keys(): return True
        if self.get_len(data_format) != -1: return True

        return False

    def get_len(self, hex_format):
        if hex_format[0] == 'h' or hex_format[0] == 'c':
            if ('hex' in hex_format) or ('chr' in hex_format):
                len_start = 3
            else:
                len_start = 1
        else:
            return -1
        if len(hex_format) <= len_start: return -1
        if not all(c in string.hexdigits for c in
                   hex_format[len_start:]): return -1

        if hex_format[0] == 'c':
            return int(hex_format[len_start:]) * 2
        else:
            return int(hex_format[len_start:])
    
    def to_hex(self, data, length=None):
        if data < 0:
            data += (2 << (length - 1))
        data %= MAXINT
        
        hex_string = hex(int(data))[2:]
        if type(length) == int:
            assert length - len(hex_string) >= 0
            return "0" * (length - len(hex_string)) + hex_string
        else:
            return hex_string
    
    def get_packet(self):
        return "%s\t%s\n" % (self.to_hex(self.sensor_id, 2),
                             self.to_hex(self.data, self.data_len))

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
        super().__init__(sensor_id, 'u16')
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
        
        return "%s\t%s\n" % (self.to_hex(self.sensor_id, 2),
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
        
        return "%s\t%s\n" % (self.to_hex(self.sensor_id, 2),
                             self.to_hex(self.data, self.data_len))
