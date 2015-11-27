# handles sensor data sorting, the command queue, and raw data storage
import struct
import string


class SensorData(object):
    def __init__(self, **sensors):
        self.sensors = sensors
        self.sensor_ids = self.init_sensor_ids(sensors)

    def init_sensor_ids(self, sensors):
        sensor_ids = {}
        for name, sensor in self.sensors.iteritems():
            sensor_ids[sensor.object_id] = name
        return sensor_ids

    def update(self, sensor_id, data):
        if sensor_id in self.sensor_ids:
            sensor = self.sensors[self.sensor_ids[sensor_id]]
            if sensor.data_len == len(data):
                sensor.data = sensor.parse(data)

    def __getitem__(self, item):
        if type(item) == str:
            return self.sensors[item]
        elif type(item) == int:
            return self.sensors[self.sensor_ids[item]]
        else:
            return None

class CommandQueue(object):
    def __init__(self, **commands):
        self.commands = commands
        self.command_ids = self.init_command_ids(self.commands)

        self.queue = []

    def init_command_ids(self, commands):
        command_ids = {}
        for name, command in self.commands.iteritems():
            command_ids[command.object_id] = name
        return command_ids

    def put(self, command, data):
        if type(command) == Command:
            self.queue.append(command.get_packet(data))
        elif type(command) == int:
            packet = self.commands[self.command_ids[command]].get_packet(data)
            self.queue.append(packet)
        elif type(command) == str:
            packet = self.commands[command].get_packet(data)
            self.queue.append(packet)

    def get(self):
        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0


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
        self.data_len = 0

    def init_formats(self, formats):
        for index in xrange(len(formats)):
            if not self.is_format(formats[index]):
                raise Exception("Invalid format name: '%s'" % formats[index])

            if (formats[index] in self.short_formats and
                        self.get_len(formats[index]) == -1):
                formats[index] = self.short_formats[formats[index]]

        return formats

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


class Command(SerialObject):
    def __init__(self, command_id, format):
        super(Command, self).__init__(command_id, [format])

        self.data_len = self.format_len[self.formats[0]]
    
    def to_hex(self, decimal):
        if 0 <= decimal < 0x10:
            return "0" + hex(decimal)[2:]
        else:
            return hex(decimal)[2:]
    
    def format_data(self, data, data_format):
        if data_format == 'bool':
            return str(int(bool(data)))

        elif data_format[0] == 'h':
            return data

        elif data_format[0] == 'c':
            return hex(ord(data))[2:]

        elif 'uint' in data_format:
            return hex(data)[2:]

        elif 'int' in data_format:
            int_size = int(data_format[3:])
            if data < 0:
                data += (2 << (int_size - 1))
            return hex(data)[2:]

        elif data_format == 'float':
            return ''.join('%.2x' % ord(c) for c in struct.pack('>f', data))

        elif data_format == 'double':
            return ''.join('%.2x' % ord(c) for c in struct.pack('>d', data))
    
    def get_packet(self, data):
        assert len(data) == self.data_len and self.data_len <= 16
        packet = self.to_hex(self.object_id) + "\t"
        packet += self.to_hex(self.data_len) + "\t"

        if type(data) == str:
            packet += self.data_len + "\n"
        elif type(data) == int:
            packet += self.to_hex(self.data_len) + "\n"
        else:
            raise Exception("Invalid data type: %s, %s" % str(data), type(data))

        return packet

class Sensor(SerialObject):
    def __init__(self, sensor_id, *formats):
        super(Sensor, self).__init__(sensor_id, formats)

        self.data_indices = self.make_indices(self.formats)
        self.data_len = self.data_indices[-1]

        assert (self.data_indices == None or
                len(self.formats) == len(self.data_indices) - 1)

        self.data = None

    def make_indices(self, formats):
        indices = [0]
        for data_format in formats:
            if self.get_len(data_format) > -1:
                length = self.get_len(data_format)
            else:
                length = self.format_len[data_format]
            indices.append(indices[-1] + length)

        return indices

    def format_hex(self, hex_string, data_format):
        if data_format == 'bool':
            return bool(int(hex_string, 16))

        elif data_format[0] == 'h':
            return hex_string

        elif data_format[0] == 'c':
            string = ""
            for index in xrange(0, len(hex_string) - 1, 2):
                string += chr(int(hex_string[index: index + 2], 16))
            return string

        elif 'uint' in data_format:
            return int(hex_string, 16)

        elif 'int' in data_format:
            bin_length = len(hex_string) * 4
            raw_int = int(hex_string, 16)
            if (raw_int >> (bin_length - 1)) == 1:
                raw_int -= 2 << (bin_length - 1)
            return raw_int

        elif data_format == 'float':
            # assure length of 8
            input_str = "0" * (8 - len(hex_string)) + hex_string

            return struct.unpack('!f', input_str.decode('hex'))[0]
        elif data_format == 'double':
            # assure length of 16
            input_str = "0" * (16 - len(hex_string)) + hex_string

            return struct.unpack('!d', input_str.decode('hex'))[0]

    def parse(self, hex_string):
        data = []
        assert len(hex_string) == self.data_len

        for index in xrange(len(self.data_indices) - 1):
            datum = hex_string[
                    self.data_indices[index]: self.data_indices[index + 1]]
            data.append(self.format_hex(datum, self.formats[index]))

        if len(data) == 1:
            return data[0]
        else:
            return data


if __name__ == '__main__':
    def almost_equal(value1, value2, epsilon=0.0005):
        if type(value1) == list and type(value2) == list:
            assert len(value1) == len(value2)
            for index in xrange(len(value1)):
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
    assert test_sensor6.parse(test_data13) == 16683798221049756444L
    assert test_sensor6.parse(test_data14) == 9750427821734154540L
    assert test_sensor6.parse(test_data15) == 17622601182450008253L

    assert test_sensor7.parse(test_data12) == 1613406758666811215
    assert test_sensor7.parse(test_data13) == -1762945852659795172L
    assert test_sensor7.parse(test_data14) == -8696316251975397076L
    assert test_sensor7.parse(test_data15) == -824142891259543363L

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

    sensor_data = SensorData(**dict(test15=test_sensor15, test16=test_sensor16))

    sensor_data.update(test_sensor15.object_id, test_data21)
    sensor_data.update(test_sensor16.object_id, test_data32)

    assert sensor_data[test_sensor15.object_id].data == test_sensor15.parse(
        test_data21)
    assert sensor_data[test_sensor16.object_id].data == test_sensor16.parse(
        test_data32)

    sensor_data.update(test_sensor15.object_id, test_data22)
    sensor_data.update(test_sensor16.object_id, test_data33)

    assert sensor_data[test_sensor15.object_id].data == test_sensor15.parse(
        test_data22)
    assert sensor_data[test_sensor16.object_id].data == test_sensor16.parse(
        test_data33)

    sensor_data.update(test_sensor15.object_id, test_data23)
    sensor_data.update(test_sensor16.object_id, test_data34)

    assert sensor_data[test_sensor15.object_id].data == test_sensor15.parse(
        test_data23)
    assert sensor_data[test_sensor16.object_id].data == test_sensor16.parse(
        test_data34)
