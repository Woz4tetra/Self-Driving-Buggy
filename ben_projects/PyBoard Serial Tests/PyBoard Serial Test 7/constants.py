

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
    'exit': 255
})