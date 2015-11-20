import serial
import time

serialRef = serial.Serial(port="/dev/cu.usbmodem1421",
                                           baudrate=115200)

def get_sensor(sensor_id):
    serialRef.write(chr(sensor_id) + "\n")
        
    data = ""
    character = ""
    while character != "\n":
        character = serialRef.read()
        data += character
    return data

def send_command(command_id, data):
    parity = command_id ^ data
    if parity <= 0xf:
        parity = "0" + hex(parity)[2:]
    else:
        parity = hex(parity)[2:]
    packet = chr(command_id) + "\t" + str(data) + "\t" + parity + "\n"
    serialRef.write(packet)

read_flag = serialRef.read()
print("Waiting for ready flag...")
time.sleep(0.5)
while read_flag != 'R':
    print read_flag
    read_flag = serialRef.read()
serialRef.write(" ");
serialRef.flushInput()
serialRef.flushOutput()
print("Arduino initialized!")
time.sleep(0.5)
serialRef.write("\n")  # packets begin and end with \n. Send this first to start the flow of data

sensor_id = 1
led13_state = True
while True:
    print sensor_id, get_sensor(sensor_id)
    sensor_id = (sensor_id % 4) + 1
    
    send_command(7, int(led13_state))
    led13_state = not led13_state
    time.sleep(0.01)

