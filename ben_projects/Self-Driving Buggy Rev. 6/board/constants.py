

class ReversibleDict:  # if repeated values occur, the most recent one is used
    def __init__(self, input_dict):
        self.dictionary = input_dict
        self.dictionary.update(ReversibleDict._reverse(input_dict))

    @staticmethod
    def _reverse(dictionary):
        reversed_dict = {}
        for key, value in dictionary.iteritems():
            reversed_dict[value] = key
        return reversed_dict

    def __getitem__(self, item):
        return self.dictionary[item]


PACKET_TYPES = ReversibleDict({
    'command':            0x01,
    'command reply':      0x02,
    'send 8-bit data':    0x03,
    'send 16-bit data':   0x04,
    'send data array':    0x05,
    'request data':       0x06,
    'request data array': 0x07,
    'exit':               0xff
})

PYBOARD_COMMAND_IDS = ReversibleDict({
    'built-in led 1': 0x00,
    'built-in led 2': 0x01,
    'built-in led 3': 0x02,
    'built-in led 4': 0x03,
    'built-in switch': 0x04,
    'built-in accelerometer': 0x05,
    'servo 1': 0x06,
    'servo 2': 0x07,
    'servo 3': 0x08,
    'servo 4': 0x09,
    'gps': 0x0A,
    'ultrasonic': 0x0B,
})

ARDUINO_COMMAND_IDS = ReversibleDict({
    'fake led': 0x01,
    'fake sensor 8 bit': 0x02,
    'fake sensor 16 bit': 0x03,
    'fake gps': 0x04,
    'fake motor': 0x05,

    'led 13': 0x0d,
})

OFF = 0
ON = 1

NODE_PC = 1
NODE_BOARD = 2