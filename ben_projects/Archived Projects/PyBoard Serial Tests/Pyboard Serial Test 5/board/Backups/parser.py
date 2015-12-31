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