def create_packet(command_type, node_id, command_id, payload):
    # T##N##I##P##Q##
    # # is number in hex
    assert 0 <= command_type <= 0xff
    assert 0 <= command_id <= 0xff
    assert 0 <= node_id <= 0xff
    
    parity = to_hex(command_type ^ node_id ^ command_id ^ payload)
    command_type = to_hex(command_type)
    command_id = to_hex(command_id)
    payload = to_hex(payload)
    node_id = to_hex(node_id)
    packet = "T" + str(command_type) + "N" + str(node_id) + "I" + str(command_id) + "P" + str(payload) + "Q" + str(parity) + "\r"
    
    return packet

def to_hex(value):
    value = hex(value)
    value = value[2:4]
    if (int(value,16) < 16):
        value = "0" + value
    
    return value
