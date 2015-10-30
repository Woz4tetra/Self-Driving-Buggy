import time
import config
from controllers.user_objects import *

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

def servo_test_command():
    while True:
        servo_value = raw_input("servo (0...180):")

        servo.set(servo_value)

def servo_test_flipper():
    while True:
        if servo.value == servo['min']:
            print("max")
            servo.set("max")
        else:
            print("min")
            servo.set("min")

        time.sleep(1)

def imu_test():
    time0 = time.time()
    while True:
        led13.set(not led13.state)

        imu.get()
        print(time.time() - time0),
        print (imu.gyroX, imu.gyroY, imu.gyroZ),
        print (imu.accelX, imu.accelY, imu.accelZ)
        # time.sleep(0.001)

if __name__ == '__main__':
    imu = IMU()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=156)
    led13 = Led13()

    initialize(True)

    # servo_test_command()
    # servo_test_flipper()
    # while True:
    #     led13.set(not led13.state)
        # time.sleep(1)

    imu_test()

    # gps.get()
    # print(gps.longitude, gps.latitude)
    # encoder.get()
    # print(encoder.distance)
