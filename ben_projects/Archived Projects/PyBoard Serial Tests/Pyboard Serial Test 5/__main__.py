
import serial
import time
import packet_maker_test

if __name__ == '__main__':
    serial_ref = serial.Serial(port="")

    payload = 0

    while True:
        packet = packet_maker_test.create_packet(0x01, 0x00, 0x02, payload)

        serial_ref.write(packet)

        payload += 1
        time.sleep(0.01)