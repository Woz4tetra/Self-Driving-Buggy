
def parse(packet):
    """Parse a packet"""
    if validate_packet(packet):
        return (parse_data(packet))
    else:
        return 0

def parse_data(packet):
    """Parse the data"""
    #        print (self.get_sensor_id(packet),
    #                " becomes ",
    #                self.converter.serial_to_db(self.get_sensor_id(packet)))
    return (get_packet_type(packet),
            get_node_id(packet),
            get_command_id(packet),
            get_payload(packet),)


def validate_packet(packet):
    """Validate an incoming packet using parity control"""
    if len(packet) == 15:
        received_parity = get_quality_check(packet)
        calculated_parity = (int(packet[1:3], 16)
                                  ^ int(packet[4:6], 16)
                                  ^ int(packet[7:9], 16)
                                  ^ int(packet[10:12], 16))
        if received_parity == calculated_parity:
            return True
    else:
        return False


def get_packet_type(packet):
    """Get the packet type"""
    if validate_packet(packet):
        if packet[0] == 'T':
            return hex_to_dec(packet[1:3])
        else:
            return 0


def get_node_id(packet):
    """Get the node id"""
    if packet[3] == 'N':
        return hex_to_dec(packet[4:6])
    else:
        return 0


def get_command_id(packet):
    """Get the command id"""
    if packet[6] == 'I':
        return hex_to_dec(packet[7:9])
    else:
        return 0


def get_payload(packet):
    """Get the payload"""
    if packet[9] == 'P':
        return hex_to_dec(packet[10:12])
    else:
        return 0


def get_quality_check(packet):
    """Get the parity 'quality check'"""
    if packet[12] == 'Q':
        return hex_to_dec(packet[13:15])
    else:
        return 0


def hex_to_dec(hexvalue):
    """Convert hex value to decimal"""
    return int(hexvalue, 16)


def test_parse():
    assert hex_to_dec("56") == 86
    assert hex_to_dec("00") == 0
    assert hex_to_dec("ff") == 255

    packet1 = create_packet(0x0, 0x0, 0x0, 0x0)[:-1]
    packet2 = create_packet(0xff, 0xff, 0xff, 0xff)[:-1]
    packet3 = create_packet(0x34, 0xe5, 0x6f, 0x65)[:-1]
    packet4 = "T34Ne5I6fP65Qbf"


    assert get_quality_check(packet1) == 0
    assert get_quality_check(packet2) == 0
    assert get_quality_check(packet3) == 0xdb

    assert get_payload(packet1) == 0
    assert get_payload(packet2) == 0xff
    assert get_payload(packet3) == 0x65

    assert get_command_id(packet1) == 0
    assert get_command_id(packet2) == 0xff
    assert get_command_id(packet3) == 0x6f

    assert get_node_id(packet1) == 0
    assert get_node_id(packet2) == 0xff
    assert get_node_id(packet3) == 0xe5

    assert get_packet_type(packet1) == 0
    assert get_packet_type(packet2) == 0xff
    assert get_packet_type(packet3) == 0x34

    assert validate_packet(packet1)
    assert validate_packet(packet2)
    assert validate_packet(packet3)

    assert parse(packet1) == (0, 0, 0, 0)
    assert parse(packet2) == (0xff, 0xff, 0xff, 0xff)
    assert parse(packet3) == (0x34, 0xe5, 0x6f, 0x65)
    assert parse(packet4) == 0


if __name__ == '__main__':
    from packet_maker_test import *

    test_parse()