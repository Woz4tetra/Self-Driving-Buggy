"""
Written by Ben Warwick

Self-Driving Buggy Rev. 6 (serial_parser.py) for Self-Driving Buggy Project
Version 9/29/2015
=========

This module handles all packet creation and verification. The conventions for
packets are detailed in Serial Packet Convention 9-23-15.numbers. Packets are
a convention of data transfer over usb serial. This is to ensure all data
arrives correctly and on time.

A summary of the convention is as follows:
T##N##I##P##Q##

T - Packet type, what kind of data is being sent?
N - Node ID, where it came from
I - Command ID, where it's going
P - Payload, the data
Q - Quality/Parity, did the packet arrive intact?

This module should be used in tandem with serial_comm.py and common.py
"""

from __future__ import print_function
from common import *
from common import _makeParity
import sys
import struct
import copy


class Parser():
    """SerialParser: parser for SerialPacket data"""
    min_length = 16

    def __init__(self):
        pass

    def parse(self, packet, verbose=False, markers=None, out='dec'):
        """Parse a packet"""
        if self._validatePacket(packet):
            return self._parseData(self.remove_newline(packet), verbose,
                                   markers, out)
        else:
            return None

    def _parseData(self, packet, verbose, markers=None, out='dec'):
        """Parse the data"""
        packet_type = self.getPacketType(packet)
        if packet_type == PACKET_TYPES['exit']:
            sys.exit(1)

        if verbose == False:
            return (self.getCommandID(packet),
                    self._parsePayload(self._getPayloadHex(packet), markers,
                                       out))
        else:
            return (packet_type,
                    self.getNodeID(packet),
                    self.getCommandID(packet),
                    self._parsePayload(self._getPayloadHex(packet), markers,
                                       out),
                    self.getQualityCheck(packet))

    def verify(self, sent_packet, received_packet):
        if len(sent_packet) == 0 or len(received_packet) == 0:
            return True  # serial is miss timed. Trying again for new packet

        sent_parsed = self.parse(sent_packet, verbose=True)
        recv_parsed = self.parse(received_packet, verbose=True)

        if sent_parsed == None or recv_parsed == None:
            return False
        sent_type, sent_node, sent_cID, sent_load, sent_parity = sent_parsed
        recv_type, recv_node, recv_cID, recv_load, recv_parity = recv_parsed

        sent_packet = self.remove_newline(sent_packet)
        received_packet = self.remove_newline(received_packet)

        if (sent_type == PACKET_TYPES['command'] and recv_type !=
            PACKET_TYPES['command reply']):
            print("packet is not reply:")
            print(repr(received_packet), repr(sent_packet))
            return False
        if (sent_type == PACKET_TYPES['request data'] and
                (recv_type != PACKET_TYPES['send 16-bit data'] and
                         recv_type != PACKET_TYPES['send 8-bit data'] and
                         recv_type != PACKET_TYPES['send data array'])):
            print("packet is not data:")
            print(repr(received_packet), repr(sent_packet))
            return False

        payload_length = len(self._getPayloadHex(received_packet))
        if (recv_type == PACKET_TYPES['send data array'] and
                    (recv_cID * 2) != payload_length):
            print("data length does not match specified")
            print("expected: ", recv_cID * 2)
            print("received: ", payload_length)
            print(repr(received_packet), repr(sent_packet))
            return False

        if sent_node != NODE_PC or recv_node != NODE_BOARD:
            print("nodes are incorrect:", sent_node, recv_node)
            return False

        if sent_cID != recv_cID and recv_type != PACKET_TYPES[
            'send data array']:
            print("command ids do not match:")
            print(repr(received_packet), repr(sent_packet))
            return False

        if sent_parity != self.getQualityCheck(sent_packet) or \
                        recv_parity != self.getQualityCheck(received_packet):
            print("incorrect parities:")
            print(repr(received_packet), repr(sent_packet))
            return False

        return True

    @staticmethod
    def remove_newline(packet):
        if packet[-2:] == '\r\n':
            return packet[:-2]
        else:
            return packet

    def _validatePacket(self, packet):
        """Validate an incoming packet using parity control"""
        if packet[-2:] != "\r\n" or len(packet) < Parser.min_length:
            return False

        packet = self.remove_newline(packet)

        self.receivedParity = self.getQualityCheck(packet)

        packet_type = self.getPacketType(packet)
        self.calculatedParity = _makeParity(packet_type,
                                            self.getNodeID(packet),
                                            self.getCommandID(packet),
                                            self.getPayload(packet))

        if self.receivedParity == self.calculatedParity:
            return True
        else:
            print("Parities did not match:")
            print(repr(packet))
            print("Received: " + hex(self.receivedParity) +
                  ", Calculated: " + hex(self.calculatedParity))
            return False

    def getPacketType(self, packet):
        """Get the packet type"""
        if packet[0] == 'T':
            return self.hex_to_dec(packet[1:3])
        else:
            print("Packet type flag 'T' not found:", repr(packet))
            return -1

    def getNodeID(self, packet):
        """Get the node id"""
        if packet[3] == 'N':
            return self.hex_to_dec(packet[4:6])
        else:
            print("Node ID flag 'N' not found:", repr(packet))
            return -1

    def getCommandID(self, packet):
        """Get the sensor id"""
        if packet[6] == 'I':
            return self.hex_to_dec(packet[7:9])
        else:
            print("Command ID flag 'I' not found:", repr(packet))
            return -1

    def getPayload(self, packet):
        """Get the payload"""
        payload = self._getPayloadHex(packet)
        if payload != -1:
            payload = self.hex_to_dec(payload)
        return payload

    def _getPayloadHex(self, packet):
        p_index = 9
        start_index = p_index + 1
        end_index = packet.find('Q')
        if packet[p_index] == 'P':
            return packet[start_index: end_index]
        else:
            print("Payload flag 'P' not found:", repr(packet))
            return -1

    def getQualityCheck(self, packet):
        """Get the parity 'quality check'"""
        q_index = len(packet) - 3  # Q##
        if packet[q_index] == 'Q':
            return self.hex_to_dec(packet[q_index + 1:])
        else:
            print("Parity/Quality flag 'Q' not found:", repr(packet),
                  packet[q_index])
            return None

    @staticmethod
    def hex_to_dec(hexvalue):
        """Convert hex value to decimal"""
        return int(hexvalue, 16)

    @staticmethod
    def _formatInt(input_str, format):
        if format == 'float':
            input_str = "0" * (8 - len(input_str)) + input_str
            return struct.unpack('!f', input_str.decode('hex'))[0]
        elif format == 'dec':
            return int(input_str, 16)
        elif format == 'bool':
            return bool(input_str)
        else:
            return input_str

    @staticmethod
    def _makeMakers(markers, length):
        markers = copy.copy(markers)

        if type(markers) == int:
            incrementer = markers
            markers = []
            for index in xrange(length, -1, -incrementer):
                markers.append(index)
        else:
            markers = list(markers)
            markers.sort(reverse=True)
        if markers[-1] != 0:
            markers.append(0)
        if markers[0] != length:
            markers.insert(0, length)

        return markers

    @staticmethod
    def _makeOutFormats(out, parsed_length):
        if type(out) == str:
            out = [out] * parsed_length

        assert len(out) == parsed_length
        return out

    def _parsePayload(self, payload, markers=None, out='dec'):
        # markers and markers are in units of digits of a hex number
        assert type(payload) == str

        parsed = []

        if markers == None:
            return self._formatInt(payload, out)
        else:
            markers = self._makeMakers(markers, len(payload))
            for index in xrange(1, len(markers)):
                parsed.insert(0, payload[markers[index]: markers[index - 1]])

            out = self._makeOutFormats(out, len(parsed))

            for index in xrange(0, len(parsed)):
                parsed[index] = self._formatInt(parsed[index], out[index])

            if len(parsed) > 1:
                return parsed
            else:
                return parsed[0]


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
    packet9 = 'T05N02I10P423a4e39410e4757Q47\r\n'
    packet10 = 'T05N02I0cP4e0b30d8b648Q58\r\n'

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
    generated_packet1 = serial_comm.Communicator.makePacket(1, 0, 0)
    generated_packet2 = serial_comm.Communicator.makePacket(1, 6, 0xb4)
    generated_packet3 = serial_comm.Communicator.makePacket(6, 4, 0)
    generated_packet4 = serial_comm.Communicator.makePacket(7, 0xa, 0)
    generated_packet5 = serial_comm.Communicator.makePacket(7, 5, 0)

    generated_packet6 = serial_comm.Communicator.makePacket(5, 0xc,
                                                            0x4e0b30d8b648)

    assert parser.parse(packet1, verbose=True) == (1, 1, 0, 0, 0x00)
    assert parser.parse(packet2, verbose=True) == (1, 1, 6, 180, 0xb2)
    assert parser.parse(packet3, verbose=True) == (6, 1, 4, 0, 0x03)
    assert parser.parse(packet4, verbose=True) == (7, 1, 10, 0, 0x0c)
    assert parser.parse(packet5, verbose=True) == (7, 1, 5, 0, 0x03)

    assert parser.parse(packet6, verbose=True) == (2, 2, 0, 1, 0x01)
    assert parser.parse(packet7, verbose=True) == (2, 2, 6, 180, 0xb2)
    assert parser.parse(packet8, verbose=True) == (3, 2, 4, 1, 0x04)
    assert parser.parse(packet9, verbose=True) == (
        5, 2, 16, 0x423a4e39410e4757, 0x47)
    assert parser.parse(packet10, verbose=True) == (
        5, 2, 12, 0x4e0b30d8b648, 0x58)

    assert parser.parse(packet11) == None
    print("Good!\n")
    assert parser.parse(packet12) == None
    print("Good!")
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
    assert generated_packet6 == "T05N01I0cP4e0b30d8b648Q5b\r\n"

    # ---- payload parsing ---- #

    packet20 = "T05N02I06PF02CC6ED01EAQ1D\r\n"
    packet21 = "T05N02I06PC07AE8D618DCQ41\r\n"
    packet22 = "T05N02I06P2D8B2ACD372DQ5A\r\n"
    packet23 = "T05N02I12P457BAD6D45F6E48A00000000000000000601Q31\r\n"
    packet24 = "T05N02I12P457BAD6D45F6E07400000000000000000601QCB\r\n"
    packet25 = "T05N02I12P457BAD6D45F8A7FA00000000000000000601Q0C\r\n"

    assert parser._parsePayload(parser._getPayloadHex(packet20), markers=3,
                                out='hex') == ['F02', 'CC6', 'ED0', '1EA']
    assert parser._parsePayload(parser._getPayloadHex(packet21), markers=3,
                                out='hex') == ['C07', 'AE8', 'D61', '8DC']
    assert parser._parsePayload(parser._getPayloadHex(packet22), markers=3,
                                out='hex') == ['2D8', 'B2A', 'CD3', '72D']

    assert parser._parsePayload(parser._getPayloadHex(packet20), markers=4,
                                out='hex') == ['F02C', 'C6ED', '01EA']
    assert parser._parsePayload(parser._getPayloadHex(packet21), markers=4,
                                out='hex') == ['C07A', 'E8D6', '18DC']
    assert parser._parsePayload(parser._getPayloadHex(packet22), markers=4,
                                out='hex') == ['2D8B', '2ACD', '372D']

    assert parser._parsePayload(parser._getPayloadHex(packet20), markers=6,
                                out='hex') == ['F02CC6', 'ED01EA']
    assert parser._parsePayload(parser._getPayloadHex(packet21), markers=6,
                                out='hex') == ['C07AE8', 'D618DC']
    assert parser._parsePayload(parser._getPayloadHex(packet22), markers=6,
                                out='hex') == ['2D8B2A', 'CD372D']

    assert parser._parsePayload(parser._getPayloadHex(packet20), markers=7,
                                out='hex') == ['F02CC', '6ED01EA']
    assert parser._parsePayload(parser._getPayloadHex(packet21), markers=7,
                                out='hex') == ['C07AE', '8D618DC']
    assert parser._parsePayload(parser._getPayloadHex(packet22), markers=7,
                                out='hex') == ['2D8B2', 'ACD372D']

    assert parser._parsePayload(parser._getPayloadHex(packet20), markers=12,
                                out='hex') == 'F02CC6ED01EA'
    assert parser._parsePayload(parser._getPayloadHex(packet21), markers=12,
                                out='hex') == 'C07AE8D618DC'
    assert parser._parsePayload(parser._getPayloadHex(packet22), markers=12,
                                out='hex') == '2D8B2ACD372D'

    assert parser._parsePayload(parser._getPayloadHex(packet20),
                                out='hex') == 'F02CC6ED01EA'
    assert parser._parsePayload(parser._getPayloadHex(packet21),
                                out='hex') == 'C07AE8D618DC'
    assert parser._parsePayload(parser._getPayloadHex(packet22),
                                out='hex') == '2D8B2ACD372D'

    assert parser._parsePayload(parser._getPayloadHex(packet20),
                                markers=(0, 4, 8, 12)) == \
           parser._parsePayload(parser._getPayloadHex(packet20), markers=(4, 8))
    assert parser._parsePayload(parser._getPayloadHex(packet21),
                                markers=(0, 4, 8, 12)) == \
           parser._parsePayload(parser._getPayloadHex(packet21), markers=(4, 8))
    assert parser._parsePayload(parser._getPayloadHex(packet22),
                                markers=(0, 4, 8, 12)) == \
           parser._parsePayload(parser._getPayloadHex(packet22), markers=(4, 8))

    assert parser._parsePayload(parser._getPayloadHex(packet23),
                                markers=[8, 16, 24, 32, 34, 36],
                                out=['float'] * 4 + ['dec'] * 2) == \
           [4026.839111328125, 7900.5673828125, 0.0, 0.0, 6, 1]
    assert parser._parsePayload(parser._getPayloadHex(packet24),
                                markers=[8, 16, 24, 32, 34, 36],
                                out=['float'] * 4 + ['dec'] * 2) == \
           [4026.839111328125, 7900.056640625, 0.0, 0.0, 6, 1]
    assert parser._parsePayload(parser._getPayloadHex(packet25),
                               markers=[8, 16, 24, 32, 34, 36],
                               out=['float'] * 4 + ['dec'] * 2) == \
           [4026.839111328125, 7956.9970703125, 0.0, 0.0, 6, 1]


if __name__ == '__main__':
    import random
    import serial_comm

    test_serial_packet()
