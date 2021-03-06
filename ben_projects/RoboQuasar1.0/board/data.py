"""
    Written by Ben Warwick

    data.py, written for RoboQuasar1.0
    Version 12/28/2015
    =========

    Handles sensor data sorting, the command queue, and raw data storage.

    Classes:
        SensorPool - parses and sorts the incoming packet by giving it to the correct sensor
        CommandQueue - A queue of Command objects. Use put to enqueue a command
        SerialObject - Internal. The superclass of Sensor and Command.
        Sensor - contains the sensor id, expected data format, and parsed sensor data
        Command - contains the command id, data format, and last sent data

    Functions:
        try_sensor - given a list of formats and a hex string, this function
            allows you to test what the output of your sensor would be
            (try with python -i data.py)
        try_command - given a single format (commands are single format)
            and a python built-in type, this functions returns the packet that
            would be written to serial
"""

import struct
import string
import random
from sys import maxsize as MAXINT


class SensorPool(object):
    def __init__(self, *sensors):
        self.sensor_index = 0
        self.sensors = {}
        #add sensors to self.sensors with non-repeating sensor IDs
        for sensor in sensors: 
            if sensor.object_id in list(self.sensors.keys()):
                raise Exception(
                        "Sensor ID already taken: " + str(sensor.object_id))
            else:
                self.sensors[sensor.object_id] = sensor
    #is_packet makes sure the packet is the right format and was safely delivered
    def is_packet(self, packet):
        if len(packet) < 4: return False
        if packet[2] != "\t": return False
        if not all(c in string.hexdigits for c in packet[0:2] + packet[3:]):
            return False

        return True
    #updates the sensors' data when called and. if correct, parses and replaces the old sensor data
    def update(self, packet):
        packet = packet.decode('ascii')
        if self.is_packet(packet):
            sensor_id, data = int(packet[0:2], 16), packet[3:]

            if sensor_id in list(self.sensors.keys()):
                sensor = self.sensors[sensor_id]

                if sensor.data_len == len(data):
                    sensor._data = sensor.parse(data)
                    sensor.current_packet = packet
        else:
            print(("Invalid packet: " + repr(packet)))

#CommandQueue creates a queue for all commands as a nice wrapper for using queues in Python
class CommandQueue(object):
    def __init__(self):
        self.queue = []

    def put(self, command):
        assert (isinstance(command, Command))
        self.queue.append(command.get_packet())

    def get(self):
        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0


def try_sensor(formats, hex_string=None):
    exp_sensor = Sensor(0, *formats)

    if hex_string == None:
        hex_string = ""
        for counter in range(exp_sensor.data_len):
            hex_string += "%0x" % (random.randint(0, 15))
        print(("Using hex data:", hex_string))

    return exp_sensor.parse(hex_string)


def try_command(command_id, data_format, data=None):
    exp_command = Command(command_id, data_format)
    print((exp_command.data_len * 4 - 2))
    if data == None:
        data = random.randint(0, int((2 << (exp_command.data_len * 4 - 2)) - 1))

    exp_command._data = data
    return exp_command.get_packet()


class SerialObject(object):
    short_formats = {
        'u8': 'uint8', 'u16': 'uint16', 'u32': 'uint32', 'u64': 'uint64',
        'i8': 'int8', 'i16': 'int16', 'i32': 'int32', 'i64': 'int64',
        'f': 'float', 
        'd': 'double',
        'b': 'bool',
        'h': 'hex', 
        'c': 'chr',
    }

    format_len = {
        'uint8': 2, 'uint16': 4, 'uint32': 8, 'uint64': 16,
        'int8': 2, 'int16': 4, 'int32': 8, 'int64': 16,
        'float': 8, 
        'double': 16,
        'bool': 1,
        'hex': None, 
        'chr': None,
    }

    #formats is the list of formats used by the serial object, 
    #for this code, the sensors are the serial objects
    def __init__(self, object_id, formats):
        assert(type(object_id) == int)
        self.formats = self.init_formats(list(formats))

        self.object_id = object_id

        self.data_len = 0
        self._data = self.init_data(self.formats)

        self.current_packet = ""

    @property
    def data(self):
        return self._data

    # @data.setter
    # def data(self, new_data):
    #     self._data = new_data

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
        if len(data) == 1: # in case data is not a list
            return data[0]
        else:
            return data

    def init_formats(self, formats):
        for index in range(len(formats)):
            if not self.is_format(formats[index]):
                raise Exception("Invalid format name: '%s'" % formats[index])
            # assigns formats from the list of short formats if it is not hex or char
            if (formats[index] in self.short_formats and
                        self.get_len(formats[index]) == -1):
                formats[index] = self.short_formats[formats[index]]

        return formats
    #is_format makes sure the data format is correct
    def is_format(self, data_format):
        if data_format in list(self.short_formats.keys()): return True
        if data_format in list(self.format_len.keys()): return True
        if self.get_len(data_format) != -1: return True

        return False
    #get_len gets the length of the format needed, returns -1 if it is not a hex or char
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

    #reformats the data as a string
    def __str__(self): 
        return "%s" % (str(self.data))

    def __repr__(self):
        str_formats = str(self.formats)[1:-1]
        return "%s(%s, %s)" % (self.__class__.__name__, self.object_id,
                               str_formats)

class Sensor(SerialObject):
    def __init__(self, sensor_id, *formats):
        super().__init__(sensor_id, formats)

        self.data_indices = self.make_indices(self.formats)
        self.data_len = self.data_indices[-1]

    #makes it easier to access each format
    def make_indices(self, formats):
        indices = [0]
        for data_format in formats:
            if self.get_len(data_format) > -1:
                length = self.get_len(data_format)
            else:
                length = self.format_len[data_format]
            indices.append(indices[-1] + length)

        return indices

    # formats each hex string according to what data format was given 
    # (see SerialObject class for list of formats)
    def format_hex(self, hex_string, data_format):
        if data_format == 'bool':
            return bool(int(hex_string, 16))

        elif data_format[0] == 'h':
            return hex_string

        elif data_format[0] == 'c':
            string = ""
            for index in range(0, len(hex_string) - 1, 2):
                string += chr(int(hex_string[index: index + 2], 16))
            return string

        elif 'uint' in data_format:
            return int(hex_string, 16)

        elif 'int' in data_format:
            bin_length = len(hex_string) * 4
            raw_int = int(hex_string, 16)
            if (raw_int >> (bin_length - 1)) == 1:
                raw_int -= 2 << (bin_length - 1)
            return int(raw_int)

        elif data_format == 'float':
            return struct.unpack('!f', bytes.fromhex(hex_string))[0]

        elif data_format == 'double':
            return struct.unpack('!d', bytes.fromhex(hex_string))[0]

    #a function to parse data, formatted into hex strings
    def parse(self, hex_string):
        data = []
        if len(hex_string) != self.data_len:
            print(("Data length does not match! Expected length %s, received %s"
                   "Ignoring: %s", str(self.data_len), str(len(hex_string)),
                   hex_string))

        for index in range(len(self.data_indices) - 1):
            datum = hex_string[
                    self.data_indices[index]: self.data_indices[index + 1]]
            data.append(self.format_hex(datum, self.formats[index]))

        if len(data) == 1:
            return data[0]
        else:
            return data

    def __repr__(self):
        if len(self.formats) > 1:
            str_formats = str(self.formats)
        else:
            str_formats = str(self.formats[0])
        return "%s(%s): %s" % (self.__class__.__name__, self.object_id,
                               str_formats)


class Command(SerialObject):
    def __init__(self, command_id, format):
        super(Command, self).__init__(command_id, [format])

        self.data_len = self.format_len[self.formats[0]]

    def to_hex(self, decimal, length):
        hex_format = "0.%sx" % length
        return ("%" + hex_format) % decimal

    # formats data for sending over serial
    def format_data(self, data, data_format):
        if data_format == 'bool':
            return str(int(bool(data)))

        elif data_format[0] == 'h':
            return data

        elif data_format[0] == 'c':
            return "%0x" % ord(data)

        elif 'uint' in data_format:
            data %= MAXINT
            return self.to_hex(data, self.data_len)

        elif 'int' in data_format:
            int_size = int(data_format[3:])
            if data < 0:
                data += (2 << (int_size - 1))

            data %= MAXINT
            return self.to_hex(data, self.data_len)

        elif data_format == 'float':
            return ''.join('%.2x' % ord(c) for c in struct.pack('>f', data))

        elif data_format == 'double':
            return ''.join('%.2x' % ord(c) for c in struct.pack('>d', data))

        else:
            raise Exception("Invalid data format: %s, %s" % str(data),
                            data_format)

    # creates the packet to send
    def get_packet(self):
        packet = self.to_hex(self.object_id, 2) + "\t"
        packet += self.to_hex(self.data_len, 2) + "\t"

        packet += self.format_data(self._data, self.formats[0]) + "\r"

        self.current_packet = packet

        return packet

    def __repr__(self):
        if len(self.formats) > 1:
            str_formats = str(self.formats)
        else:
            str_formats = str(self.formats[0])
        return "%s(%s): %s" % (self.__class__.__name__, self.object_id,
                               str_formats)

#########################################################################################
#########                               TEST CASES                                #######
#########################################################################################

# almost-equal is a function created to compare floats to assert the code is correct

if __name__ == '__main__':
    def almost_equal(value1, value2, epsilon=0.0005):
        if type(value1) == list and type(value2) == list:
            # assert len(value1) == len(value2)
            for index in range(len(value1)):
                if type(value1[index]) == float or type(value2[index]) == float:
                    if abs(value1[index] - value2[index]) > epsilon:
                        return False
                else:
                    if value1[index] != value2[index]:
                        return False
            return True
        else:
            return abs(value1 - value2) <= epsilon


    test_data0 = 'f1'
    test_data1 = '61'
    test_data2 = '80'
    test_data3 = '98'

    test_data4 = '100a'
    test_data5 = '31b9'
    test_data6 = '8fe4'
    test_data7 = '13d9'

    test_data8 = '4cc8ce5e'
    test_data9 = 'bbd68285'
    test_data10 = 'b40a3a22'
    test_data11 = 'c9f014df'

    test_data12 = '1663f8e6188cb74f'
    test_data13 = 'e788c21665f6fb1c'
    test_data14 = '87507a71a28cd12c'
    test_data15 = 'f4900e682a4fc0bd'

    test_data16 = '736f6d657468696e67'  # "something" in hex
    test_data17 = '736f6d657468696e6720696e746572657374696e67'  # "something interesting" in hex

    test_data18 = '0'
    test_data19 = '1'
    test_data20 = 'f'

    test_data21 = 'bb82983a8f70'
    test_data22 = 'e41b0ab0ec9d'
    test_data23 = 'fb799c9ea125'

    test_data24 = 'c62d5854'
    test_data25 = '4604533d'
    test_data26 = '4655a8d2'
    test_data27 = '45c222d2'

    test_data28 = 'c1dd3020fd42f18a'
    test_data29 = 'c1df7a298419c69f'
    test_data30 = '41bd292405635331'
    test_data31 = '41b8745ae2bb8ec9'

    test_data32 = 'c1e648ca4107b783c33c1180c3be27de4cf3'
    test_data33 = 'c76facfb43ccad3ac7448bc146ba6fa75d2f'
    test_data34 = 'c71f288bc4a82617c61e308d467f126e506a'

    test_data35 = '4861707079205468616E6B73676976696E67210A'

    test_sensor0 = Sensor(0, 'u8')
    test_sensor1 = Sensor(1, 'i8')
    test_sensor2 = Sensor(2, 'u16')
    test_sensor3 = Sensor(3, 'i16')
    test_sensor4 = Sensor(4, 'u32')
    test_sensor5 = Sensor(5, 'i32')
    test_sensor6 = Sensor(6, 'u64')
    test_sensor7 = Sensor(7, 'i64')
    test_sensor8 = Sensor(8, 'f')
    test_sensor9 = Sensor(9, 'd')
    test_sensor10 = Sensor(10, 'b')
    test_sensor11 = Sensor(11, 'h8')
    test_sensor12 = Sensor(12, 'c1')
    test_sensor13 = Sensor(13, 'c9')
    test_sensor14 = Sensor(14, 'c21')

    test_sensor15 = Sensor(15, 'i16', 'i16', 'i16')
    test_sensor16 = Sensor(16, 'f', 'f', 'f', 'f', 'u8', 'u8')

    test_sensor17 = Sensor(14, 'c20')

    assert test_sensor0.parse(test_data0) == 241
    assert test_sensor0.parse(test_data1) == 97
    assert test_sensor0.parse(test_data2) == 128
    assert test_sensor0.parse(test_data3) == 152

    assert test_sensor1.parse(test_data0) == -15
    assert test_sensor1.parse(test_data1) == 97
    assert test_sensor1.parse(test_data2) == -128
    assert test_sensor1.parse(test_data3) == -104

    assert test_sensor2.parse(test_data4) == 4106
    assert test_sensor2.parse(test_data5) == 12729
    assert test_sensor2.parse(test_data6) == 36836
    assert test_sensor2.parse(test_data7) == 5081

    assert test_sensor3.parse(test_data4) == 4106
    assert test_sensor3.parse(test_data5) == 12729
    assert test_sensor3.parse(test_data6) == -28700
    assert test_sensor3.parse(test_data7) == 5081

    assert test_sensor4.parse(test_data8) == 1288228446
    assert test_sensor4.parse(test_data9) == 3151397509
    assert test_sensor4.parse(test_data10) == 3020569122
    assert test_sensor4.parse(test_data11) == 3387954399

    assert test_sensor5.parse(test_data8) == 1288228446
    assert test_sensor5.parse(test_data9) == -1143569787
    assert test_sensor5.parse(test_data10) == -1274398174
    assert test_sensor5.parse(test_data11) == -907012897

    assert test_sensor6.parse(test_data12) == 1613406758666811215
    assert test_sensor6.parse(test_data13) == 16683798221049756444
    assert test_sensor6.parse(test_data14) == 9750427821734154540
    assert test_sensor6.parse(test_data15) == 17622601182450008253

    assert test_sensor7.parse(test_data12) == 1613406758666811215
    assert test_sensor7.parse(test_data13) == -1762945852659795172
    assert test_sensor7.parse(test_data14) == -8696316251975397076
    assert test_sensor7.parse(test_data15) == -824142891259543363

    assert almost_equal(test_sensor8.parse(test_data24), -11094.081624888348)
    assert almost_equal(test_sensor8.parse(test_data25), 8468.80986213082)
    assert almost_equal(test_sensor8.parse(test_data26), 13674.205209398357)
    assert almost_equal(test_sensor8.parse(test_data27), 6212.352615283554)

    assert almost_equal(test_sensor9.parse(test_data28), -1958773749.0459924)
    assert almost_equal(test_sensor9.parse(test_data29), -2112398864.4027479)
    assert almost_equal(test_sensor9.parse(test_data30), 489235461.38798815)
    assert almost_equal(test_sensor9.parse(test_data31), 410278626.7326475)

    assert test_sensor10.parse(test_data18) == False
    assert test_sensor10.parse(test_data19) == True
    assert test_sensor10.parse(test_data20) == True

    assert test_sensor11.parse(test_data8) == '4cc8ce5e'
    assert test_sensor11.parse(test_data9) == 'bbd68285'
    assert test_sensor11.parse(test_data10) == 'b40a3a22'
    assert test_sensor11.parse(test_data11) == 'c9f014df'

    assert test_sensor12.parse(test_data0) == '\xf1'
    assert test_sensor12.parse(test_data1) == 'a'
    assert test_sensor12.parse(test_data2) == '\x80'
    assert test_sensor12.parse(test_data3) == '\x98'

    assert test_sensor13.parse(test_data16) == "something"

    assert test_sensor14.parse(test_data17) == "something interesting"

    assert test_sensor17.parse(test_data35) == "Happy Thanksgiving!\n"

    assert test_sensor15.parse(test_data21) == [-17534, -26566, -28816]
    assert test_sensor15.parse(test_data22) == [-7141, 2736, -4963]
    assert test_sensor15.parse(test_data23) == [-1159, -25442, -24283]

    assert almost_equal(test_sensor16.parse(test_data32),
                        [-28.7855406751, 8.48230229985,
                         -188.068366832, -380.311456783,
                         76, 243])
    assert almost_equal(test_sensor16.parse(test_data33),
                        [-61356.98, 409.35333,
                         -50315.754, 23863.826,
                         93, 47])
    assert almost_equal(test_sensor16.parse(test_data34),
                        [-40744.543, -1345.1903,
                         -10124.138, 16324.607,
                         80, 106])

    sensor_data = SensorPool(test_sensor15, test_sensor16)

    sensor_data.update("%0.2x\t%s" % (15, test_data21))
    sensor_data.update("%0.2x\t%s" % (16, test_data32))

    assert sensor_data.sensors[
               test_sensor15.object_id].data == test_sensor15.parse(
            test_data21)
    assert sensor_data.sensors[
               test_sensor16.object_id].data == test_sensor16.parse(
            test_data32)

    sensor_data.update("%0.2x\t%s" % (15, test_data22))
    sensor_data.update("%0.2x\t%s" % (16, test_data33))

    assert sensor_data.sensors[
               test_sensor15.object_id].data == test_sensor15.parse(
            test_data22)
    assert sensor_data.sensors[
               test_sensor16.object_id].data == test_sensor16.parse(
            test_data33)

    sensor_data.update("%0.2x\t%s" % (15, test_data23))
    sensor_data.update("%0.2x\t%s" % (16, test_data34))

    assert sensor_data.sensors[
               test_sensor15.object_id].data == test_sensor15.parse(
            test_data23)
    assert sensor_data.sensors[
               test_sensor16.object_id].data == test_sensor16.parse(
            test_data34)
