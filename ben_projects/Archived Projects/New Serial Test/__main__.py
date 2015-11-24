'''
    Written by Ben Warwick
    
    New Serial Test for Self-Driving Buggy Project
    Version 11/14/2015
    =========
    
    This program a new implementation of the serial protocol using
    multithreading. Possibly for Self-Driving Buggy Rev. 7
    
    Usage
    -----
    python __main__.py
    - or - (in folder directory):
    python New\ Serial\ Test/
    
'''

import arduino_object
import serial_comm
import time


def run():
    # magnet = arduino_object.Sensor("MAGNET",
    #                                "#### #### ####",
    #                                "int")
    # gyro = arduino_object.Sensor("GYRO",
    #                              "#### #### ####",
    #                              "int")
    # accel = arduino_object.Sensor("ACCEL",
    #                               "#### #### ####",
    #                               "int")
    # gps = arduino_object.Sensor("GPS",
    #                             "######## ######## ######## ######## ## ##",
    #                             "ffffuu")
    encoder = arduino_object.Sensor("ENCODER",
                                    "########")
    # servo = arduino_object.Command("SERVO")
    led13 = arduino_object.Command("LED13")

    encoder.sensor_ids["ENCODER"] = 5
    led13.command_ids["LED13"] = 7

    serial_ref = serial_comm.SerialRef(115200, 0)
    # serial_ref = serial_comm.SimulatedSerial(0.5)
    commander = serial_comm.CommandThread(serial_ref)
    receiver = serial_comm.DataThread(serial_ref, [encoder])#[magnet, gyro, accel, gps, encoder])

    commander.start()
    receiver.start()

    # servo_value = 0
    led13_value = True

    try:
        while True:
            # commander.put(servo, servo_value)
            # servo_value += 1

            commander.put(led13, int(led13_value))
            led13_value = not led13_value

            # print("encoder:", encoder.data)
            # print("gps:", gps.data)
            # print("accel:", accel.data)
            # print("encoder:", encoder.data)

            time.sleep(0.5)
    except KeyboardInterrupt:
        commander.stop()
        receiver.stop()


if __name__ == '__main__':
    print __doc__
    run()
