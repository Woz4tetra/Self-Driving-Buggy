from board import serial_comm
from board import serial_parser
from board.common import PACKET_TYPES

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

        self.dataLength = 0
        if markers != None:
            for character in markers:
                if character == "#":
                    self.dataLength += 1

    def send(self, payload=0):
        self._sentPacket = communicator.makePacket(self.packetType,
                                                   self.commandID,
                                                   payload)
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

    def get(self):
        if self.send():
            return self.result
        else:
            return None


class Setter(ArduinoObject):
    def __init__(self, command_id, out_format='dec'):
        super(Setter, self).__init__('command', command_id, None, out_format)

    def set(self, value):
        return self.send(value)

# ArduinoObject.used_command_ids = ["ACCELGYRO_ID", "ENCODER_ID", "SERVO_ID",
#                                   "GPS_ID", "LED13_ID"]
# add_defines()
