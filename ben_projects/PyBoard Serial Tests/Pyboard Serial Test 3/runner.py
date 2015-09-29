import serial
import time

# ---- start pyboard, pc similarity ----

start_char = chr(0)
end_char = chr(1)
char_range = [2, 256] # [2, 256) (2...256 exclusive)

def to_digits(n, b):
    """Convert a positive number n to its digit representation in base b."""
    if n == 0:
        return [char_range[0]]
    digits = []

    if n < 0:
        digits.insert(0, "-")
        n = abs(n)

    while n > 0:
        digits.insert(0, chr(n % b + char_range[0]))
        n = n // b
    return digits

def make_instructions(data):
    byte_list = [start_char]
    byte_list += reversed(to_digits(data, char_range[1] - char_range[0]))
    byte_list.append(end_char)
    return byte_list

def unwrap_instructions(byte_list):
    data = 0
    for index in xrange(len(byte_list)):
        data += (ord(byte_list[index]) - char_range[0]) * (char_range[1] - char_range[0]) ** index
    return data

def write_instructions(serial_ref, byte_list):
    for byte in byte_list:
        serial_ref.write(byte)

# ---- end pyboard, pc similarity ----

def read_instructions(serial_ref):
    char = serial_ref.read()
    while char != bytes(start_char):
        char = serial_ref.read()
        print repr(char),
    
    byte_list = []
    while char != bytes(end_char):
        char = serial_ref.read()
        byte_list.append(char)
    print byte_list
    return byte_list

def handshake(serial_ref):
    char = serial_ref.read()
    while char != 'P':
        serial_ref.write('R')
        char = serial_ref.read()
        print char,

def send_flag(serial_ref, flag):
    assert 0 <= ord(flag) <= 255
    serial_ref.write(flag)

#for index in xrange(1000):
#    time0 = time.time()
#    read_instructions(make_instructions(10 ** index)[1:-1])
#    time1 = time.time()
#    print time1 - time0

if __name__ == '__main__':
    ser = serial.Serial('/dev/cu.usbmodem1412', 9600, timeout=0.001)
    handshake(ser)
    
    print "handshake complete"
    
    counter = 1
    while True:
        ser.write(b'a')
        
        if counter % 100 == 0:
            print unwrap_instructions(read_instructions(ser))
        counter += 1
        time.sleep(0.001)

