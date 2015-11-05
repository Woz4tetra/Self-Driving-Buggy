from board import serial_comm
from board import serial_parser
from board.common import PACKET_TYPES
import config

communicator = serial_comm.Communicator()
parser = serial_parser.Parser()

def start():
    communicator.start()


class ArduinoObject(object):
    used_command_ids = []

    def __init__(self, packet_type, command_id, markers, out_formats):
        assert type(command_id) == str
        assert command_id not in ArduinoObject.used_command_ids
        assert packet_type in PACKET_TYPES.keys()

        ArduinoObject.used_command_ids.append(command_id)

        self.packetType = PACKET_TYPES[packet_type]
        self.commandID = ArduinoObject.used_command_ids.index(command_id)
        self.markers = markers
        self.out_formats = out_formats

        self._sentPacket = ""
        self._recvPacket = ""

        self.result = None
        
        self._currentPayload = 0

        self.dataLength = 0
        if markers != None:
            for character in markers:
                if character == "#":
                    self.dataLength += 1

    def send(self, payload=0):
        self._sentPacket = communicator.makePacket(self.packetType,
                                                   self.commandID,
                                                   payload)

        if self._sentPacket != communicator.currentPacket:
            communicator.write(self._sentPacket)
        
        self._recvPacket = communicator.read()
        
        verified = parser.verify(self._sentPacket, self._recvPacket,
                                 self.dataLength)

        if verified:
            self.result = parser.parse(self._recvPacket,
                                       markers=self.markers,
                                       out=self.out_formats)

        return verified


class Getter(ArduinoObject):
    def __init__(self, command_id, markers=None, out_formats='dec'):
        super(Getter, self).__init__('request data', command_id, markers,
                                     out_formats)

    def get(self, *args):
        if self.send():
            return self.result
        else:
            return None


class Setter(ArduinoObject):
    def __init__(self, command_id, out_format='dec'):
        super(Setter, self).__init__('command', command_id, None, out_format)

    def set(self, value):
        return self.send(value)


def _add_defines(file_name):
    project_dir = config.get_arduino_dir(file_name)
    with open(project_dir, 'r') as serial_box_file:
        contents = serial_box_file.read()

        start_ids = contents.find("/* Command IDs start */")
        end_ids = contents.find("/* Command IDs end */", start_ids)

        assert start_ids != -1 and start_ids < end_ids

        defines = "/* Command IDs start */\n"

        for index in xrange(len(ArduinoObject.used_command_ids)):
            if index < 0x10:
                value = "0x0" + hex(index)[2:]
            else:
                value = hex(index)[0:2]

            defines += "#define " + ArduinoObject.used_command_ids[
                index] + "_ID " + value + "\n"

        defines += "/* Command IDs end */\n"

        start_enables = contents.find("/* Enables start */")
        end_enables = contents.find("/* Enables end */", start_enables)

        assert start_enables != -1 and start_enables < end_enables

        enables = "/* Enables start */\n"

        for index in xrange(len(ArduinoObject.used_command_ids)):
            enables += "#define ENABLE_" + ArduinoObject.used_command_ids[
                index] + "\n"

        contents = contents[0: start_ids] + \
                   defines + "\n\n" + \
                   enables + \
                   contents[end_enables:]
    with open(project_dir, 'w') as serial_box_file:
        serial_box_file.write(contents)

# ArduinoObject.used_command_ids = ["ACCELGYRO_ID", "ENCODER_ID", "SERVO_ID",
#                                   "GPS_ID", "LED13_ID"]
# add_defines()
