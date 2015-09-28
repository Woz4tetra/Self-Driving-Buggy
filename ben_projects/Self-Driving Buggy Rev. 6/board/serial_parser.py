"""

"""

from __future__ import print_function
from constants import *
import sys


class Parser():
    """SerialParser: parser for SerialPacket data"""

    def __init__(self):
        pass

    def parse(self, packet):
        """Parse a packet"""
        if self.validatePacket(packet):
            return self.parseData(packet[:-2])
        else:
            return None

    def verify(self, sent_packet, received_packet):
        sent_type, sent_node, sent_cID, sent_load, sent_parity = \
            self.parseData(sent_packet, verbose=True)
        recv_type, recv_node, recv_cID, recv_load, recv_parity = \
            self.parseData(received_packet, verbose=True)

        if (sent_type == PACKET_TYPES['command'] and recv_type !=
                PACKET_TYPES['command reply']):
            print("packet is not reply")
            return False
        if (sent_type == PACKET_TYPES['request data'] and
                (recv_type != PACKET_TYPES['send 16-bit data'] and
                 recv_type != PACKET_TYPES['send 8-bit data'])):
            print("packet is not 16 or 8 bit")
            return False
        if (sent_type == PACKET_TYPES['request data array'] and
                 recv_type != PACKET_TYPES['send data array']):
            print("packet is not array")
            return False

        if sent_node != NODE_PC or recv_node != NODE_BOARD:
            print("nodes are incorrect:", sent_node, recv_node)
            return False

        if sent_cID != recv_cID:
            print("command ids do not match")
            return False

        if sent_parity != self.getQualityCheck(sent_packet) or \
                recv_parity != self.getQualityCheck(received_packet):
            print("incorrect parities")
            return False

        return True

    def parseData(self, packet, verbose=False):
        """Parse the data"""
        packet_type = self.getPacketType(packet)
        if packet_type == PACKET_TYPES['exit']:
            sys.exit(1)

        if verbose == False:
            return (self.getNodeID(packet),
                    self.getCommandID(packet),
                    self.getPayload(packet, packet_type))
        else:
            return (packet_type,
                    self.getNodeID(packet),
                    self.getCommandID(packet),
                    self.getPayload(packet, packet_type),
                    self.getQualityCheck(packet))

    def validatePacket(self, packet):
        """Validate an incoming packet using parity control"""
        if packet[-2:] != "\r\n" or len(packet) < 17:
            return False

        packet = packet[:-2]

        self.receivedParity = self.getQualityCheck(packet)

        packet_type = self.getPacketType(packet)
        self.calculatedParity = (packet_type ^
                                 self.getNodeID(packet) ^
                                 self.getCommandID(packet) ^
                                 self.getPayload(packet, packet_type)) & 0xff

        return self.receivedParity == self.calculatedParity

    def getPacketType(self, packet):
        """Get the packet type"""
        if packet[0] == 'T':
            return self.hex_to_dec(packet[1:3])
        else:
            return -1

    def getNodeID(self, packet):
        """Get the node id"""
        if packet[3] == 'N':
            return self.hex_to_dec(packet[4:6])
        else:
            return -1

    def getCommandID(self, packet):
        """Get the sensor id"""
        if packet[6] == 'I':
            return self.hex_to_dec(packet[7:9])
        else:
            return -1

    def getPayload(self, packet, packet_type):
        """Get the payload"""
        if (packet_type == PACKET_TYPES['command'] or
                    packet_type == PACKET_TYPES['command reply'] or
                    packet_type == PACKET_TYPES['send 8-bit data'] or
                    packet_type == PACKET_TYPES['request data'] or
                    packet_type == PACKET_TYPES['request data array'] or
                    packet_type == PACKET_TYPES['exit']):
            length = 2  # 16 * 2 = 32 bits, 8 bytes (hex character = 16 bits)
        elif packet_type == PACKET_TYPES['send 16-bit data']:
            length = 4
        elif packet_type == PACKET_TYPES['send data array']:
            length = self.getCommandID(packet)
        else:
            length = 0

        p_index = 9
        if packet[p_index] == 'P':
            return self.hex_to_dec(packet[p_index + 1: (p_index + 1) + length])
        else:
            return -1

    def getQualityCheck(self, packet):
        """Get the parity 'quality check'"""
        q_index = len(packet) - 3
        if packet[q_index] == 'Q':
            return self.hex_to_dec(packet[q_index + 1:])
        else:
            return None

    @staticmethod
    def hex_to_dec(hexvalue):
        """Convert hex value to decimal"""
        return int(hexvalue, 16)


def test_serial_packet():
    parser = Parser()

    for number in xrange(0xff):
        assert parser.hex_to_dec(hex(number)) == number

    # ---- correct packets ---- #
    packet1 = 'T01N01I00P00Q00\r\n'
    packet2 = 'T01N01I06Pb4Qb2\r\n'
    packet3 = 'T06N01I04P00Q03\r\n'
    packet4 = 'T07N01I0aP00Q0c\r\n'
    packet5 = 'T07N01I05P00Q03\r\n'

    packet6 = 'T02N02I00P01Q01\r\n'
    packet7 = 'T02N02I06Pb4Qb2\r\n'
    packet8 = 'T03N02I04P01Q04\r\n'
    packet9 = 'T05N02I10P423a4e39410e4757Q40\r\n'
    packet10 = 'T05N02I0cP4e0b30d8b648Q43\r\n'

    # ---- incorrect packets ---- #
    # send data array length (I) is 5 instead of 8
    # Note: 'I' is only length when sending data arrays
    packet11 = 'T05N02I05PdeadbeefQb1\r\n'

    # Payload not 8-bits and packet type is 'command'
    packet12 = 'T02N02I00P333Q01\r\n'

    # Missing carriage return and newline characters
    packet13 = 'T02N02I06Pb4Qb2'

    # packet10 shifted 4 characters
    packet14 = "42\r\nT04N01I10P423a4e39410e4757Q"

    # empty
    packet15 = ""
    packet16 = "\r\n"

    # garbage
    packet17 = """Traceback (most recent call last):
          File "/Users/Woz4tetra/Documents/Self-Driving-Buggy/ben_projects/PyBoard Serial Tests/PyBoard Serial Test 7/serial_parser.py", line 196, in <module>
            test_serialparser()
          File "/Users/Woz4tetra/Documents/Self-Driving-Buggy/ben_projects/PyBoard Serial Tests/PyBoard Serial Test 7/serial_parser.py", line 192, in test_serialparser
            assert parser.parse(packet16) == "something"
        AssertionError"""
    packet18 = 'all last):\r\nFile "'

    # random
    packet19 = ""
    for counter in xrange(18):
        packet19 += random.choice(["0", "1", "2", "3", "4", "5", "6", "7",
                                   "8", "9", "a", "b", "c", "d", "e", "f",
                                   "\r", "\n",
                                   "T", "N", "I", "P", "Q"])

    # ---- direct inverse ---- #
    packet_maker = serial_comm.Communicator()
    generated_packet1 = packet_maker.makePacket(1, 0, 0)
    generated_packet2 = packet_maker.makePacket(1, 6, 0xb4)
    generated_packet3 = packet_maker.makePacket(6, 4, 0)
    generated_packet4 = packet_maker.makePacket(7, 0xa, 0)
    generated_packet5 = packet_maker.makePacket(7, 5, 0)

    generated_packet6 = packet_maker.makePacket(5, 0xc, 0x4e0b30d8b648)

    assert parser.parse(packet1) == (1, 0, 0)
    assert parser.parse(packet2) == (1, 6, 180)
    assert parser.parse(packet3) == (1, 4, 0)
    assert parser.parse(packet4) == (1, 10, 0)
    assert parser.parse(packet5) == (1, 5, 0)

    assert parser.parse(packet6) == (2, 0, 1)
    assert parser.parse(packet7) == (2, 6, 180)
    assert parser.parse(packet8) == (2, 4, 1)
    assert parser.parse(packet9) == (2, 16, 0x423a4e39410e4757)
    assert parser.parse(packet10) == (2, 12, 0x4e0b30d8b648)

    assert parser.parse(packet11) == None
    assert parser.parse(packet12) == None
    assert parser.parse(packet13) == None
    assert parser.parse(packet14) == None
    assert parser.parse(packet15) == None
    assert parser.parse(packet16) == None
    assert parser.parse(packet17) == None
    assert parser.parse(packet18) == None
    if parser.parse(packet19) != None:
        print(packet19), parser.parse(packet19)
        raise AssertionError

    assert generated_packet1 == packet1
    assert generated_packet2 == packet2
    assert generated_packet3 == packet3
    assert generated_packet4 == packet4
    assert generated_packet5 == packet5
    assert generated_packet6 == "T05N01I0cP4e0b30d8b648Q40\r\n"


if __name__ == '__main__':
    import random
    import serial_comm

    test_serial_packet()
