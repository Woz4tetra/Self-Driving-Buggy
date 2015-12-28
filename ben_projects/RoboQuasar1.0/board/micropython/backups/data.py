
import struct
import array
from sys import maxsize as MAXINT

class SensorQueue(object):
    def __init__(self, *sensors):
        self.sensor_index = 0
        self.sensors = {}

        for sensor in sensors:
            if sensor.object_id in list(self.sensors.keys()):
                raise Exception(
                    "Sensor ID already taken: " + str(sensor.object_id))
            else:
                self.sensors[sensor.object_id] = sensor
        
        self.sensor_ids = sorted(self.sensors.keys())
    
    def current_index(self):
        sensor_id = self.sensor_ids[self.sensor_index]
        self.sensor_index = (self.sensor_index + 1) % len(self.sensor_ids)
        return sensor_id
    
    def get(self):
        return self.sensors[self.current_index()].get_packet()

class CommandPool(object):
    def __init__(self, *commands):
        self.commands = {}

        for command in commands:
            if command.object_id in list(self.commands.keys()):
                raise Exception(
                    "Command ID already taken: " + str(command.object_id))
            else:
                self.commands[command.object_id] = command
    
    @staticmethod
    def is_hex(character):
        return (ord('0') <= ord(character) <= ord('9') or
                ord('a') <= ord(character) <= ord('f') or
                ord('A') <= ord(character) <= ord('F'))
    
    @staticmethod
    def is_packet(packet):
        if len(packet) < 7: return False
        for index in [0, 1, 3, 4] + list(range(6, len(packet) - 1)):
            if not CommandPool.is_hex(packet[index]):
                return False
        return True
    
    def update(self, packet):
        if self.is_packet(packet):
            command_id = int(packet[0:2], 16)
            data_len = int(packet[3:5], 16)
            hex_data = packet[6: data_len + 6]
            
            if len(hex_data) == data_len:
                data = self.commands[command_id].format_data(hex_data)
                self.commands[command_id].callback(data)
        

class SerialObject(object):
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
    
    def __init__(self, object_id, formats):
        self.formats = self.init_formats(list(formats))
        
        self.object_id = object_id
        
        self.data_len = self.get_data_len(self.formats)
        self.data = init_data(self.formats)
    
    def init_data(self, formats):
        data = []
        for format in formats:
            if format[0] == 'i' or format[0] == 'u':
                data.append(0)
            elif format[0] == 'f' or format[0] == 'd':
                data.append(0.0)
            elif format[0] == 'b':
                data.append(False)
            elif format[0] == 'h' or format[0] == 'c':
                data.append('0')
        return data
    
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
        if data_format in list(self.short_formats.keys()): return True
        if data_format in list(self.format_len.keys()): return True
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
    

class Sensor(SerialObject):
    def __init__(self, sensor_id, *formats):
        super().__init__(sensor_id, formats)
    
    def to_hex(self, data, length=0):
        if type(data) == int:
            if data < 0 and length > 0:
                data += (2 << (length * 4 - 1))
            data %= MAXINT
        
            hex_format = "0.%sx" % length
            return ("%" + hex_format) % data
        else:
            raise Exception("Data not int type")
    
    def float_to_hex(self, data):
        return "%0.8x" % (struct.unpack('<I', bytes(array.array('f', [data]))))
    
    def format_data(self):
        hex_string = ""
        # length of data should equal number of formats
        for index in range(len(formats)):
            if format[0] == 'f' or format[0] == 'd':
                hex_string += self.float_to_hex(self.data[index])
            else:
                hex_string += self.to_hex(data[index], self.format_len[format])
        return hex_string
    
    def update_data(self):
        pass
    
    def get_packet(self):
        self.update_data()
        return "%s\t%s\r" % (self.to_hex(self.object_id, 2),
                             self.format_data())

class Command(SerialObject):
    def __init__(self, command_id, format):
        super().__init__(command_id, [format])
    
    def format_data(self, hex_string):
        if self.formats[0] == 'bool':
            return bool(int(hex_string, 16))

        elif self.formats[0][0] == 'h':
            return hex_string

        elif self.formats[0][0] == 'c':
            string = ""
            for index in range(0, len(hex_string) - 1, 2):
                string += chr(int(hex_string[index: index + 2], 16))
            return string

        elif 'uint' in self.formats[0]:
            return int(hex_string, 16)

        elif 'int' in self.formats[0]:
            bin_length = len(hex_string) * 4
            raw_int = int(hex_string, 16)
            if (raw_int >> (bin_length - 1)) == 1:
                raw_int -= 2 << (bin_length - 1)
            return int(raw_int)

        elif self.formats[0] == 'float':
            # assure length of 8
            input_str = "0" * (8 - len(hex_string)) + hex_string

            return struct.unpack('!f', input_str.decode('hex'))[0]
        elif self.formats[0] == 'double':
            # assure length of 16
            input_str = "0" * (16 - len(hex_string)) + hex_string

            return struct.unpack('!d', input_str.decode('hex'))[0]
    
    def callback(self, data):
        pass

