from controllers.user_objects import *

if __name__ == '__main__':
    angle_sensor = Magnetometer()
    gps = GPS()
    encoder = Encoder()
    servo = Servo(min=0, max=156)
    led13 = Led13()

    initialize("SerialBox.ino", 115200)