from board import serial_comm
from board import serial_parser
from board.common import PACKET_TYPES
from board import file_generator
import config

communicator = serial_comm.Communicator()
parser = serial_parser.Parser()

def initialize(ino_file="SerialBox", baud_rate=115200, arduino_node=2, delay=0.004):
    file_generator.generate_file(ino_file,
                                 ArduinoObject.command_ids,
                                 baud_rate, arduino_node)

    key = raw_input("Please upload sketch (or enter 'q' to quit): ")
    if key == 'q':
        quit()
    
    communicator.start(baud_rate, delay)


class ArduinoObject(object):
    command_ids = []

    def __init__(self, packet_type, command_id, markers, out_formats):
        assert type(command_id) == str
        assert command_id not in ArduinoObject.command_ids
        assert packet_type in PACKET_TYPES.keys()

        ArduinoObject.command_ids.append(command_id)

        self.packetType = PACKET_TYPES[packet_type]
        self.commandID = command_id
        self.markers = markers
        self.out_formats = out_formats

        self._sentPacket = ""
        self._recvPacket = ""

        self.result = None
        
        self._currentPayload = 0

        self.is_disabled = False

        self.dataLength = 0
        if markers != None:
            for character in markers:
                if character == "#":
                    self.dataLength += 1

    def send(self, payload=0):
        if not self.is_disabled:
            command_id = ArduinoObject.command_ids.index(self.commandID)
            self._sentPacket = communicator.makePacket(self.packetType,
                                                       command_id,
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
        else:
            return False

    def disable(self):
        ArduinoObject.command_ids.remove(self.commandID)
        self.is_disabled = True



class Getter(ArduinoObject):
    def __init__(self, command_id, markers=None, out_formats='uint'):
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
