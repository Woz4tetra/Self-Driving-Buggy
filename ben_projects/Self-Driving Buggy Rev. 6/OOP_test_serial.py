import time
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
            servo.set("max")
        else:
            servo.set("min")

        time.sleep(1)

def imu_test():
    # time_total = 0
    while True:
        # time0 = time.time()
        # led13.set(not led13.state)

        # print accel_gyro.get()
        print magnet.get()
        # time1 = time.time()
        # time_total += time1 - time0
        
        # print time_total
        # print (accel_gyro.gyroX, accel_gyro.gyroY, accel_gyro.gyroZ),
        # print (accel_gyro.accelX, accel_gyro.accelY, accel_gyro.accelZ)
        # print (magnet.x, magnet.y, magnet.z)
        # time.sleep(0.001)

def led13_test():
    while True:
        led13.set(not led13.state)
        time.sleep(0.01)

def gps_test():
    while True:
        gps.get()
        print(gps.longitude, gps.latitude)

if __name__ == '__main__':
    accel_gyro = AccelGyro()
    magnet = Magnet()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=156)
    led13 = Led13()

    initialize()

    # servo_test_command()
    # servo_test_flipper()

    # led13_test()
    imu_test()

    # gps_test()
    # encoder.get()
    # print(encoder.distance)
