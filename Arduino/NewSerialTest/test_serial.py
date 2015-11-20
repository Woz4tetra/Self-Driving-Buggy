import serial
import time

serialRef = serial.Serial(port="/dev/cu.usbmodem1421",
                                           baudrate=115200)

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

sensor_id = 5
led13_state = True
while True:
    if sensor_id == 5:
        serialRef.write(chr(sensor_id) + "\n")
        print "wrote:", repr(chr(sensor_id) + "\n")
    
        data = ""
        character = ""
        while character != "\n":
            character = serialRef.read()
            data += character
        print "data:", repr(data)
    else:
        parity = sensor_id ^ int(led13_state)
        if parity <= 0xf:
            parity = "0" + hex(parity)[2:]
        else:
            parity = hex(parity)[2:]
        packet = chr(sensor_id) + "\t" + str(int(led13_state)) + "\t" + parity + "\n"
        print "wrote:", repr(packet)
        serialRef.write(packet)
        led13_state = not led13_state
        time.sleep(0.01)
    

    if sensor_id == 5:
        sensor_id = 7
    else:
        sensor_id = 5
#    time.sleep(0.01)
#    sensor_id = (sensor_id % 5) + 1
#    print sensor_id
