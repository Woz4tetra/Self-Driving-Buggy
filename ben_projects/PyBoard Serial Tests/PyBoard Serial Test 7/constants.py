

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
    'command': 0,
    'command reply': 1,
    'send 8-bit data': 2,
    'send 16-bit data': 3,
    'send data array': 4,
    'request data': 5,
    'request data array': 6,
    'exit': 0xff
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
    'something interesting 1': 0x00,
    'something interesting 2': 0x01,
})

ON = 1
OFF = 2