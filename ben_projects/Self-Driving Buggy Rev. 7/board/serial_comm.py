import serial
import struct
import string
import time

address = "/dev/cu.usbmodem1411"
#"/dev/cu.usbmodem1421"
#"/dev/cu.usbmodem1411"

serialRef = serial.Serial(port=address, baudrate=115200)

def makeParity(node, object_id, data):
    parity = int(node, 16) ^ int(object_id, 16)
    
    while len(data) > 0:
        parity ^= int(data[0:2], 16)
        data = data[2:]
    return parity
        
def splitMarkers(data, markers):
    split_data = []
    
    for marker in markers.split(" "):
        assert len(data) > 0

        datum = data[0: len(marker)]
        split_data.append(datum)

        data = data[len(marker):]

    return split_data

def parseData(data, markers, out_formats):
    result = []
    if markers != None:
        data = splitMarkers(data, markers)
    
    
    for index in xrange(len(data)):
        if type(out_formats) == str:
            result.append(formatInt(data[index], out_formats))
        else:
            result.append(formatInt(data[index], out_formats[index]))
    if len(result) == 1:
        result = result[0]
    return result

def formatInt(input_str, format):
    if format == 'float':
        input_str = "0" * (8 - len(input_str)) + input_str
        return struct.unpack('!f', input_str.decode('hex'))[0]
    elif format == 'int':
        bin_length = len(input_str) * 4
        raw_int = int(input_str, 16)
        if (raw_int >> (bin_length - 1)) == 1:
            raw_int -= 2 ** bin_length
        return raw_int
    elif format == 'uint':
        return int(input_str, 16)
    elif format == 'bool':
        return bool(int(input_str))
    else:
        return input_str

def get_sensor(sensor_id, markers, out_formats):
    out_formats = convertOuts(out_formats)
    
    serialRef.write(chr(sensor_id) + "\n")
#    print repr(chr(sensor_id) + "\n")
    
    packet = []
    data = ""
    character = ""
    while character != "\n":
        character = serialRef.read()
        if character != '\t' and character != '\n':
            if character in string.hexdigits:
                data += character
            else:
                data += hex(ord(character))[2:]
        else:
            packet.append(data)
            data = ""
    
#    print repr(packet)
#    if len(packet) != 4: return None
#    if int(packet[0], 16) != 2: return None
#    if int(packet[1], 16) != sensor_id: return None
#    if int(packet[3], 16) != makeParity(*packet[0:3]):
#        return None
    return packet
    #parseData(packet[2], markers, out_formats)

def send_command(command_id, data):
    parity = command_id ^ data
    if parity <= 0xf:
        parity = "0" + hex(parity)[2:]
    else:
        parity = hex(parity)[2:]
    packet = chr(command_id) + "\t" + (hex(data)[2:])[::-1] + "\t" + parity + "\n"
#    print(repr(packet))
    serialRef.write(packet)

formats = {
    'u': 'uint',
    'i': 'int',
    'h': 'hex',
    'f': 'float',
    'b': 'bool'
}

def convertOuts(out_formats):
    if out_formats == None:
        return 'uint'
    if out_formats in formats.values():
        return out_formats
    
    out_list = []
    for character in out_formats:
        if character in formats:
            out_list.append(formats[character])
        else:
            raise Exception("""Invalid format: %s
                Valid characters:
                %s
                """ % (character, formats))
    return out_list

def handshake():
    read_flag = serialRef.read()
    print("Waiting for ready flag...")
    time.sleep(0.5)
    while read_flag != 'R':
        print read_flag,
        read_flag = serialRef.read()
    serialRef.write(" ");
    serialRef.flushInput()
    serialRef.flushOutput()
    print("Arduino initialized!")
    time.sleep(0.5)
    serialRef.write("\n")  # packets begin and end with \n. Send this first to start the flow of data
