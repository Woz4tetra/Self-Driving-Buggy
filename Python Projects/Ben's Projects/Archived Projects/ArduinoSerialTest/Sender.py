import serial, time

arduino = serial.Serial('/dev/cu.usbmodem1411', 115200, timeout=.1)
time.sleep(1)  # give the connection a second to settle
# arduino.write("Hello from Python!")
value = 0
delta = 1

while True:
    data = arduino.readline()
    if data:
        print data.rstrip('\n') # strip out the new lines for now
        # (better to do .read() in the long run for this reason

    time.sleep(0.001)
    arduino.write("CH")
    if (value == 180):
        delta = -1
    elif (value == 0):
        delta = 1
    value += delta
    value = 180 if value == 0 else 0