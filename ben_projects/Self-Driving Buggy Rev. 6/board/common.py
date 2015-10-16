
# Types of data that can be sent over serial
PACKET_TYPES = {
    'command':            0x01,
    'command reply':      0x02,
    'send 8-bit data':    0x03,
    'send 16-bit data':   0x04,
    'send data array':    0x05,
    'request data':       0x06,
    'exit':               0xff
}

OFF = 0
ON = 1

NODE_PC = 1
NODE_BOARD = 2

# Creates the parity of the packet. Used by serial_comm.py and serial_parser.py
def _makeParity(packet_type, node, command_id, payload):
    if type(payload) == str:
        payload = int(payload, 16)

    main_parity = packet_type ^ node ^ command_id
    payload_parity = payload & 0xff  # order does not matter
    if packet_type == PACKET_TYPES['send data array']:
        while payload > 0:
            payload = payload >> 8
            payload_parity ^= payload & 0xff
    return main_parity ^ payload_parity
