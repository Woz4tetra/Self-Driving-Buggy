import threading

from constants import PACKET_TYPES

class SerialCommunication(threading.Thread):
    def __init__(self):

        super(SerialCommunication, self).__init__()

    def run(self):
        while True:
            pass

    def sendPacket(self):
        pass

    def makePacket(self, packet_type, command_id, payload):
        if (packet_type == PACKET_TYPES['command'] or
                    packet_type == PACKET_TYPES['command reply'] or
                    packet_type == PACKET_TYPES['send 8-bit data'] or
                    packet_type == PACKET_TYPES['request data'] or
                    packet_type == PACKET_TYPES['request data array'] or
                    packet_type == PACKET_TYPES['exit']):
            length = 2  # 4 * 2 = 8 bits
        elif packet_type == PACKET_TYPES['send 16-bit data']:
            length = 4
        elif packet_type == PACKET_TYPES['send data array']:
            length = None
        else:
            length = 0

        T = self.format_element(packet_type)
        N = self.format_element(0)
        I = self.format_element(command_id)
        P = self.format_element(payload, length)
        Q = self.format_element((packet_type ^ 0x00 ^ command_id ^ payload) & 0xff)

        return "T{}N{}I{}P{}Q{}\r\n".format(T, N, I, P, Q)

    @staticmethod
    def format_element(packet_element, digits=2):
        assert type(packet_element) == int
        if digits < 2 and digits != None:
            digits = 2
        if (packet_element < 16):
            return "0" + hex(packet_element)[-1:]
        elif digits == None:
            return hex(packet_element)[2:]
        else:
            return hex(packet_element)[-digits:]