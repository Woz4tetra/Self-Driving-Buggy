import struct

next_id = 0

class ArduinoObject(object):
    formats = {
        'u': 'uint',
        'i': 'int',
        'h': 'hex',
        'f': 'float',
        'b': 'bool'
    }

    def __init__(self, name, markers=None, out_formats='uint'):
        self.name = name

        self.markers = markers
        self.out_formats = self.convertOuts(out_formats)

        self._sentPacket = ""
        self._recvPacket = ""

        self.data = 0

        self.dataLength = 0
        if markers != None:
            for character in markers:
                if character == "#":
                    self.dataLength += 1
                elif character != " ":
                    raise Exception("Invalid marker character: " + character)

    def convertOuts(self, out_formats):
        if out_formats == None:
            return 'uint'
        if out_formats in self.formats.values():
            return out_formats

        out_list = []
        for character in out_formats:
            if character in self.formats:
                out_list.append(self.formats[character])
            else:
                raise Exception("""Invalid format: %s
Valid characters:
%s
""" % character, self.formats)
        return out_list

    def __str__(self):
        return self.name

    def makeParity(self, node, object_id, data):
        parity = int(node, 16) ^ int(object_id, 16)

        for index in xrange(len(data) - 1, -1, 2):
            parity ^= int(data[index: index - 2], 16)

        return parity

    def update(self, data):
        self.data = data


class Sensor(ArduinoObject):
    sensor_ids = {}
    def __init__(self, name, markers=None, out_formats='uint', node=2):
        global next_id

        self.node = node

        Sensor.sensor_ids[name] = next_id
        next_id += 1
        if (chr(next_id) == '\n' or
                chr(next_id) == '\r' or
                chr(next_id) == '\t'):
            next_id += 1

        super(Sensor, self).__init__(name, markers, out_formats)

    def parse(self, packet):
        # print(repr(packet))
        split_packet = packet.split("\t")

        # print((len(split_packet), 4),
        #       (split_packet[0], self.node),
        #       (split_packet[1], self.sensor_ids[self.name]),
        #       (split_packet[3], self.makeParity(*split_packet[0:3])))

        if len(split_packet) != 4: return None
        if int(split_packet[0], 16) != self.node: return None
        if int(split_packet[1], 16) != self.sensor_ids[self.name]: return None
        if int(split_packet[3], 16) != self.makeParity(*split_packet[0:3]):
            return None

        # print("verified")
        return self.parseData(split_packet[2])

    def splitMarkers(self, data):
        split_data = []

        print(self.markers, data)
        for marker in self.markers.split(" "):
            assert len(data) > 0

            datum = data[0: len(marker)]
            split_data.append(datum)

            data = data[len(marker):]

        return split_data

    def parseData(self, data):
        result = []
        # if type(self.out_formats) == str:
        #     for index in xrange(len(data)):
        #         result.append(self.formatInt(data[index],
        #                                      self.out_formats))
        # else:
        if self.markers != None:
            data = self.splitMarkers(data)

        for index in xrange(len(data)):
            if type(self.out_formats) == str:
                result.append(self.formatInt(data[index],
                                             self.out_formats))
            else:
                result.append(self.formatInt(data[index],
                                             self.out_formats[index]))
        if len(result) == 1:
            result = result[0]
        return result

    def formatInt(self, input_str, format):
        if format == 'float':
            input_str = "0" * (8 - len(input_str)) + input_str
            return struct.unpack('!f', input_str.decode('hex'))[0]
        elif format == 'int':
            bin_length = len(input_str) * 4
            raw_int = int(input_str, 16)
            if (raw_int >> (bin_length - 1)) == 1:
                raw_int -= 2 ** bin_length
            return raw_int
        elif format == 'uint':
            return int(input_str, 16)
        elif format == 'bool':
            return bool(int(input_str))
        else:
            return input_str

    def get(self):
        return self.data

    def __str__(self):
        return chr(self.sensor_ids[self.name]) + "\r\n"


class Command(ArduinoObject):
    command_ids = {}

    def __init__(self, name):
        global next_id

        Command.command_ids[name] = next_id
        next_id += 1
        if (chr(next_id) == '\n' or
                chr(next_id) == '\r' or
                chr(next_id) == '\t'):
            next_id += 1

        super(Command, self).__init__(name)

    def set(self, value):
        self.data = str(value)

    def __str__(self):
        return "\t".join([self.command_ids[self.name],
                          self.data,
                          self.command_ids[self.name] ^ self.data,
                          "\r\n"])
