
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

# # Types of sensors and actuators on the pyboard that receive and send packets
# PYBOARD_COMMAND_IDS = {
#     'built-in led 1': 0x00,
#     'built-in led 2': 0x01,
#     'built-in led 3': 0x02,
#     'built-in led 4': 0x03,
#     'built-in switch': 0x04,
#     'built-in accelerometer': 0x05,
#     'servo 1': 0x06,
#     'servo 2': 0x07,
#     'servo 3': 0x08,
#     'servo 4': 0x09,
#     'gps': 0x0A,
#     'ultrasonic': 0x0B,
# }
#
# # Types of sensors and actuators on the arduino that receive and send packets
# ARDUINO_COMMAND_IDS = {
#     'accel gyro': 0x00,
#     'encoder': 0x01,
#     'servo': 0x02,
#     'gps': 0x03,
#     'led 13': 0x04
# }
#
# # Used for sensors that return data arrays. These indices mark data separation
# # in the "payload" section of the packet (rightmost index is zero)
# PARSE_MARKERS = {
#     'accel gyro': [4, 8, 12, 20, 28, 36],
#     'encoder': None,
#     'servo': None,
#     'gps': [8, 16, 24, 32, 34, 36],
#     'led 13': None
# }
#
# # The output formats for each sensor corresponding to the segmentations marked
# # by PARSE_MARKERS
# PARSE_OUT_FORMATS = {
#     'accel gyro': ['dec'] * 3 + ['float'] * 3,
#     'encoder': 'dec',
#     'servo': 'dec',
#     'gps': ['float'] * 4 + ['dec'] * 2,
#     'led 13': 'bool'
# }
#
# OFF = 0
# ON = 1

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
