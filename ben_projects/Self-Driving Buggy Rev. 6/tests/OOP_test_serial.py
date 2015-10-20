import time
from controllers.user_objects import *

'''
if __debug__:
   if not expression: raise AssertionError

- or -

assert

__debug__ is true if -O is not passed
'''

if __name__ == '__main__':
    imu = IMU()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=180)
    led13 = Led13()

    initialize(False)

    # counter = 0

    while True:
        # imu.get()
        # print(imu.accelX, imu.accelY, imu.accelZ,
        #       imu.gyroX, imu.gyroY, imu.gyroZ)
        # gps.get()
        # print(gps.longitude, gps.latitude)
        # encoder.get()
        # print(encoder.distance)

        servo_value = raw_input("servo (0...180):")

        servo.set(int(servo_value))
        # if counter == 20:
        #     if servo.value == servo['min']:
        #         servo.set("max")
        #     else:
        #         servo.set("min")
        #     led13.set(not led13.state)
        #     counter = 0
        # counter += 1
        time.sleep(0.001)
